from sqlalchemy import select

import database
from models import Guild

async def get_guild(guild_id: int) -> Guild:
    async with database.get_session() as session:
        result = await session.execute(
            select(Guild).where(Guild.discord_id == guild_id)
        )
        guild = result.scalars().first()
        if not guild:
            guild = Guild(discord_id=guild_id)
            session.add(guild)
            await session.commit()
            await session.refresh(guild)
        return guild

async def change_enabled(guild: Guild, enabled: bool) -> None:
    async with database.get_session() as session:
        result = await session.execute(
            select(Guild).where(Guild.id == guild.id)
        )
        guild_db = result.scalars().first()
        if guild_db:
            guild_db.enabled = enabled
            await session.commit()
