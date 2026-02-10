from sqlalchemy import Column, String, Float, Text, Boolean
from app.database import Base


class Cafe(Base):
    __tablename__ = "cafes"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    city = Column(String, nullable=False, index=True)
    district = Column(String, index=True)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    url = Column(String)
    mrt = Column(String)
    mrt_station = Column(String, index=True)
    bus_stop = Column(String)
    open_time = Column(Text)

    # Cafe Nomad ratings (0-5 scale)
    wifi = Column(Float, default=0)
    socket = Column(Float, default=0)
    quiet = Column(Float, default=0)
    tasty = Column(Float, default=0)
    cheap = Column(Float, default=0)
    music = Column(Float, default=0)
    seat = Column(Float, default=0)
    price = Column(Float)
    quiet_level = Column(String)
    has_wifi = Column(Boolean, default=False)
    has_socket = Column(Boolean, default=False)
    reservable = Column(Boolean)

    # Special features
    limited_time = Column(String)  # "yes", "no", "maybe"
    standing_desk = Column(String)  # "yes", "no"
