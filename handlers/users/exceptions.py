import asyncio
import logging

from aiogram import Router

from aiogram.exceptions import TelegramBadRequest, TelegramNetworkError, TelegramRetryAfter, TelegramAPIError
from aiogram.types.error_event import ErrorEvent

from aiogram_dialog.api.exceptions import UnknownIntent, UnknownState

from utils.main.db import write_admins_log

router = Router()


@router.errors()
async def error(event: ErrorEvent):
    if isinstance(event.exception, TelegramBadRequest):
        write_admins_log(f'ERROR TelegramBadRequest:', f'{event.exception}: {event.update}')
        return True
    if isinstance(event.exception, TelegramNetworkError):
        write_admins_log(f'ERROR TelegramNetworkError:', f'{event.exception}: {event.update}')
        return True
    if isinstance(event.exception, TelegramRetryAfter):
        write_admins_log(f'ERROR TelegramRetryAfter:', f'{event.exception}: {event.update}')
        await asyncio.sleep(event.exception.retry_after)
        return True
    if isinstance(event.exception, TelegramAPIError):
        write_admins_log(f'ERROR TelegramAPIError:', f'{event.exception}: {event.update}')
        return True

    if isinstance(event.exception, UnknownState):
        try:
            await event.update.callback_query.answer(
                "Это сообщение недоступно!", show_alert=True
            )
        except:

            return True
        return True
    if isinstance(event.exception, UnknownIntent):
        try:
            await event.update.callback_query.answer(
                "Это сообщение недоступно!", show_alert=True
            )
        except:

            return True
        return True
    logging.exception(f'{event.exception}: {event.update}', exc_info=True)
    try:
        return True
    except Exception as e:
        print(e)
