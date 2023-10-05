from sqlalchemy import Column, Integer, String, Float, Date
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Bookings(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, index=True)
    booking_date = Column(Date)
    length_of_stay = Column(Integer)
    guest_name = Column(String)
    daily_rate = Column(Float)
