from sqlalchemy import Column, Integer, String
from app.database import Base

class URL(Base):
    __tablename__ = "urls"
    id = Column(Integer, primary_key=True, index=True)
    target_url = Column(String, unique=True, index=True, nullable=False)
    short_code = Column(String, unique=True, index=True, nullable=False)
    clicks = Column(Integer, default=0)

def __repr__(self):
    return f"<URL(short_code={self.short_code}, target_url={self.target_url}, clicks={self.clicks})>"

