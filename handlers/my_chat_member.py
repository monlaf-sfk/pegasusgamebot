from contextlib import suppress

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.chat_member_updated import \
    ChatMemberUpdatedFilter, MEMBER, KICKED

from aiogram.types import ChatMemberUpdated

from loader import bot
from utils.main.users import User

router = Router()
router.my_chat_member.filter(F.chat.type == "private")
router.message.filter(F.chat.type == "private")


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=KICKED)
)
async def user_blocked_bot(event: ChatMemberUpdated):
    user = User(id=event.from_user.id)
    user.edit('blocked', True)
    if user.ref is not None:
        user_ref = User(id=user.ref)
        user_ref.edit('refs', user_ref.refs - 1)


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=MEMBER)
)
async def user_unblocked_bot(event: ChatMemberUpdated):
    user = User(id=event.from_user.id)
    user.edit('blocked', False)
    if user.ref is not None:
        user_ref = User(id=user.ref)
        user_ref.edit('refs', user_ref.refs + 1)
