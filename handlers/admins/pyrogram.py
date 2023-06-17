from contextlib import suppress

from pyrogram import Client
from pyrogram.errors.exceptions import UsernameInvalid, UsernameNotOccupied
import config

api_id = 22418508
api_hash = "06cb4dc0f493da9b138e6cc69576955e"


async def get_user_id(username):
    async with Client("pegasus", api_id=api_id, api_hash=api_hash, bot_token=config.token) as app:
        try:
            with suppress(UsernameInvalid, UsernameNotOccupied):
                user = await app.get_users(username[0])
                return user.id
        except:
            try:
                chat = await app.get_chat(username[0])
                return chat.id
            except:
                return None
