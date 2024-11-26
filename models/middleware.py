from typing import Callable, Dict, Any, Awaitable

from aiogram.types import TelegramObject
from models.db_context import DBContext
       
class InjectDBContextMiddleware:
    def __init__(self):
           self.db_context  = DBContext()        

    async def __call__(self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
           
        data["db_context"] = self.db_context
        await handler(event, data)