from datetime import datetime, timezone

from aiogram import Router, F, flags
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from filters.admin import IsOwner
from keyboard.schedule import schedue_kb, ScheduleCallback

from utils.schedulers import autopromo_run, shedualer, btc_change_run, boss_spavn_run, NYC

router = Router()


@router.message(Command("schedule"), IsOwner())
@flags.rate_limit(rate=1, key='promo_handler')
async def run_schedule_handler(message: Message):
    lol = shedualer.get_job(btc_change_run.id).next_run_time - datetime.now(timezone.utc)
    xd = f'{lol.days // 30} месяц{"ев" if lol.days // 30 > 1 else ""}' if lol.days > 30 else f'{lol.days} дней' if lol.days > 0 else f'{int(lol.seconds // 3600)} часов' \
        if lol.seconds >= 3600 else f'{int(lol.seconds // 60)} минут' if lol.seconds >= 60 else f'{lol.seconds} секунд'

    lol = shedualer.get_job(boss_spavn_run.id).next_run_time - datetime.now(timezone.utc)
    xd2 = f'{lol.days // 30} месяц{"ев" if lol.days // 30 > 1 else ""}' if lol.days > 30 else f'{lol.days} дней' if lol.days > 0 else f'{int(lol.seconds // 3600)} часов' \
        if lol.seconds >= 3600 else f'{int(lol.seconds // 60)} минут' if lol.seconds >= 60 else f'{lol.seconds} секунд'

    lol = shedualer.get_job(autopromo_run.id).next_run_time - datetime.now(timezone.utc)
    xd3 = f'{lol.days // 30} месяц{"ев" if lol.days // 30 > 1 else ""}' if lol.days > 30 else f'{lol.days} дней' if lol.days > 0 else f'{int(lol.seconds // 3600)} часов' \
        if lol.seconds >= 3600 else f'{int(lol.seconds // 60)} минут' if lol.seconds >= 60 else f'{lol.seconds} секунд'
    return await message.reply(
        f'До смены курса: {xd}\n'
        f'До спавна босса: {xd2}\n'
        f'До поста с промо: {xd3}'
        f'', reply_markup=schedue_kb(message.from_user.id))


@router.callback_query(ScheduleCallback.filter())
async def run_schedule_handler(call: CallbackQuery, callback_data: ScheduleCallback):
    if call.from_user.id != callback_data.user_id:
        return await call.answer(
            f'Руки убрал от кнопки!')
    if callback_data.action == "boss_spavn":
        job = shedualer.get_job(boss_spavn_run.id)
        await job.func()
        return await call.answer(
            f'Босс за спавлен!', show_alert=True)
    elif callback_data.action == "autopromo_run":
        job = shedualer.get_job(autopromo_run.id)
        await job.func()
        return await call.answer(
            f'Промо пост отправлен!', show_alert=True)
    elif callback_data.action == "btc_change_run":
        job = shedualer.get_job(btc_change_run.id)
        await job.func()
        return await call.answer(
            f'Курс биткоина евро юаня сменен!', show_alert=True)
