#!/usr/bin/env python3

import asyncio
import getpass
import os

import bcrypt
from dotenv import load_dotenv
from sqlalchemy import URL, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()


database_url = URL.create(
    drivername="postgresql+asyncpg",
    username=os.getenv("POSTGRES_USER"),
    password=os.getenv("POSTGRES_PASSWORD"),
    host=os.getenv("POSTGRES_HOST"),
    port=os.getenv("POSTGRES_PORT"),
    database=os.getenv("POSTGRES_DB"),
)


async def main() -> None:
    # Запрашиваем данные у пользователя
    name = input("Введите имя супер-администратора: ")
    username = input("Введите username (минимум 5 символов): ")
    password = getpass.getpass("Введите пароль (минимум 8 символов): ")

    if len(username) < 5:
        print("Username должен содержать минимум 5 символов")
        return

    if len(password) < 8:
        print("Пароль должен содержать минимум 8 символов")
        return

    hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    # Создаем подключение к БД
    engine = create_async_engine(database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        try:
            await session.execute(
                text(
                    "INSERT INTO users.admin (name, username, password, is_super_admin) "
                    "VALUES (:name, :username, :password, :is_super_admin)"
                ),
                {
                    "name": name,
                    "username": username,
                    "password": hashed_password,
                    "is_super_admin": True,
                },
            )
            await session.commit()
            print(f"Супер-администратор {name} успешно создан!")
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при создании супер-администратора: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
