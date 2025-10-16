from typing import Optional, Any

from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView


## Akeeper 16.10.2025
class BaseModelView(ModelView):
    @staticmethod
    async def show_info_modal(request: Request, message: str, data: Optional[str] = None):
        request.session['show_info_modal'] = True
        request.session['info_modal_data'] = {"message": message, "data": data}

    @staticmethod
    def is_super_admin(request: Request) -> bool | Any:
        user = getattr(request.state, 'user', None)
        if not user:
            return False

        return getattr(user, 'is_super_admin', False)

## ~Akeeper
