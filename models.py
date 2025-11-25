from sqlalchemy import Column, Integer, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Guild(Base):
    __tablename__ = "guilds"

    id = Column(Integer, primary_key=True)
    discord_id = Column(Integer, unique=True, nullable=False)
    enabled = Column(Boolean, default=False, nullable=False)
    # replace_diacritics = Column(Boolean, default=False, nullable=False)
    # remove_not_letters = Column(Boolean, default=False, nullable=False)
    # reversed_detection = Column(Boolean, default=False, nullable=False)

    def __repr__(self) -> str:
        return f"<Guild id={self.id} discord_id={self.discord_id} enabled={self.enabled}>"
