from sqlalchemy import Column, String, Float, Text
from app.database import Base


class Cafe(Base):
    __tablename__ = "cafes"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False, index=True)
    district = Column(String, index=True)  # 行政區 (e.g. "大安區")
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    url = Column(String)
    mrt = Column(String)  # Normalized MRT station name
    open_time = Column(Text)

    # Cafe Nomad ratings (0-5 scale, kept for data integrity)
    wifi = Column(Float, default=0)
    socket = Column(Float, default=0)
    quiet = Column(Float, default=0)
    tasty = Column(Float, default=0)
    cheap = Column(Float, default=0)
    music = Column(Float, default=0)
    seat = Column(Float, default=0)

    # Special features
    limited_time = Column(String)  # "yes", "no", "maybe"
    standing_desk = Column(String)  # "yes", "no"
    has_reservation = Column(String, default="")  # "yes", "no", ""
