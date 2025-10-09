from typing import Final

from aiogram import Router

from . import common

router: Final[Router] = Router(name=__name__)
router.include_routers(common.router)
