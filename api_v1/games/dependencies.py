from sqlalchemy.ext.asyncio import AsyncSession


async def check_if_game_exists(game_id: int, session: AsyncSession):
    query = select(Game).where(Game.id==game_id).exists()
    return await session.scalar(select(query))