from datetime import date
from typing import Optional

from pydantic import BaseModel


class GetBookings(BaseModel):
    id: int
    booking_date: date
    length_of_stay: int
    guest_name: str
    daily_rate: float


class GetStats(BaseModel):
    total_number_of_bookings: int
    average_length_of_stay: float
    average_daily_rate: float
    number_of_cancelled_bookings: int
    number_of_non_cancelled_bookings: int
    the_most_popular_market_segment: str


class GetAnalysis(BaseModel):
    most_popular_arrive_month: str
    least_popular_arrive_month: str
    most_popular_booking_month: str
    least_popular_booking_month: str
    all_guest_without_children: int
    all_guest_with_children_or_babyes: int
    couple_without_children_and_babyes: int
    lonely_guest: int
    percentage_of_people_with_a_parking_space: float
    most_popular_countries_by_order: dict[str, int]
    meal_packages: dict[str, int]


class PopularMealPackage(BaseModel):
    the_most_popular_meal_package: str


class AvgLengthOfStay(BaseModel):
    year: int
    hotel: str
    avg_length_of_stay: float


class TotalRevenue(BaseModel):
    month: str
    hotel: str
    total_revenue: float


class Country(BaseModel):
    country: str
    count_of_bookings: int


class AvgDailyRateResort(BaseModel):
    month: str
    avg_daily: float


class RepGuestPrecent(BaseModel):
    repeated_guests_percentage: float


class TotalGuestByYear(BaseModel):
    year: int
    count_guests: int


class RepeatGuest(BaseModel):
    hotel: str
    is_repeat: int
    count_guests: int


class TotalRevenueByCountry(BaseModel):
    country: str
    total_revenue: float


class CountMeal(BaseModel):
    hotel: str
    meal: str
    counts: int


class MostCommonArrivalDayCity(BaseModel):
    day_of_the_week: str
    counts_of_arrivals: int


class AllBookings(BaseModel):
    hotel: str
    is_canceled: int
    lead_time: int
    arrival_date_year: int
    arrival_date_month: str
    arrival_date_week_number: int
    arrival_date_day_of_month: int
    stays_in_weekend_nights: int
    stays_in_week_nights: int
    adults: int
    children: Optional[float]
    babies: int
    meal: str
    country: Optional[str]
    market_segment: str
    distribution_channel: str
    is_repeated_guest: int
    previous_cancellations: int
    previous_bookings_not_canceled: int
    reserved_room_type: str
    assigned_room_type: str
    booking_changes: int
    deposit_type: str
    agent: Optional[float]
    company: Optional[float]
    days_in_waiting_list: int
    customer_type: str
    adr: float
    required_car_parking_spaces: int
    total_of_special_requests: int
    reservation_status: str
    reservation_status_date: str
    name: str
    email: str
    phone_number: str
    credit_card: str
