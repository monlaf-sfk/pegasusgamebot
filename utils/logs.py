from aiofile import async_open


async def readlogs():
    async with async_open('assets/last.txt', 'r') as file:
        text = await file.read()
    return text


async def writefile(fetch):
    async with async_open('assets/db.txt', 'a') as file:
        return await file.write(f'{fetch}\n')


async def writelog(user_id: int, log: str):
    async with async_open('assets/last.txt', 'a') as file:
        return await file.write(f'{user_id}:{log}\n')
