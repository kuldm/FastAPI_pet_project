from datetime import datetime

import pandas as pd
from pandas import DataFrame, to_datetime

from typing import Annotated, List

from fastapi import Query, APIRouter, Depends, HTTPException

from sqlalchemy import select, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from endpoints.depends import read_csv_bookings
from endpoints.shemas import GetBookings, AllBookings, GetStats, PopularMealPackage, AvgDailyRateResort, GetAnalysis, \
    RepGuestPrecent, Country, RepeatGuest, TotalRevenue, CountMeal, MostCommonArrivalDayCity, TotalGuestByYear, \
    TotalRevenueByCountry, AvgLengthOfStay

from security.security import verify_credentials

from db import models
from db.models import Bookings
from db.database import engine, get_db

router = APIRouter()

models.Base.metadata.create_all(bind=engine)


@router.get('/bookings',
            response_model=List[GetBookings],
            tags=['Main functionalities'],
            description='Endpoint retrieves a list of all bookings in the dataset.')
async def get_bookings(db: Session = Depends(get_db)) -> List[GetBookings]:
    try:
        # Checking the connection to the database
        db.execute(text("SELECT 1"))
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

    result = db.scalars(select(Bookings).limit(50)).all()
    return [GetBookings(**r.__dict__) for r in result]


@router.get('/bookings/search',
            response_model=List[GetBookings],
            tags=['Main functionalities'],
            description='Endpoint allows searching for bookings based on various parameters such as guest name, booking'
                        ' dates, length of stay.')
async def search_bookings(guest_name: str = Query(None),
                          booking_date: str = Query(None),
                          length_of_stay: int = Query(None),
                          db: Session = Depends(get_db)) -> List[GetBookings]:
    if guest_name:
        if not guest_name.replace(" ", "").isalpha():
            raise HTTPException(status_code=400, detail='Guest name must contain only letters')

    if booking_date:
        try:
            datetime.strptime(booking_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Should be YYYY-MM-DD")

    if length_of_stay is not None and length_of_stay <= 0:
        raise HTTPException(status_code=400, detail='Length of stay cannot be less then 1')

    try:
        # Checking the connection to the database
        db.execute(text("SELECT 1"))
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

    query = db.query(Bookings)

    if guest_name or booking_date or length_of_stay:
        if guest_name:
            query = query.filter(Bookings.guest_name.contains(guest_name))

        if booking_date:
            query = query.filter(Bookings.booking_date == booking_date)

        if length_of_stay:
            query = query.filter(Bookings.length_of_stay == length_of_stay)
    else:
        raise HTTPException(status_code=400, detail="Nothing was found. Specify the search criteria.")

    bookings = query.limit(50).all()

    if not bookings:
        raise HTTPException(status_code=404, detail="Nothing was found according to the specified criteria.")

    return [GetBookings(**b.__dict__) for b in bookings]


@router.get('/bookings/stats',
            response_model=list[GetStats],
            tags=['Main functionalities'],
            description='Endpoint provides statistical information about the dataset, such as the total number of'
                        ' bookings, average length of stay, average daily rate, etc.')
async def stats_bookings(df: DataFrame = Depends(read_csv_bookings)) -> list[GetStats]:
    total_number_of_bookings = len(df)

    df['length_of_stay'] = df['stays_in_weekend_nights'].astype(int) + df['stays_in_week_nights'].astype(int)
    sum_length_of_stay = df['length_of_stay'].sum()

    sum_daily_rate = df['adr'].sum()

    average_length_of_stay = sum_length_of_stay / total_number_of_bookings
    average_daily_rate = sum_daily_rate / total_number_of_bookings

    number_of_cancelled_bookings = df['is_canceled'].sum() / 1
    number_of_non_cancelled_bookings = int(len(df) - number_of_cancelled_bookings)

    the_most_popular_market_segment = df['market_segment'].value_counts().index[0]

    return [
        GetStats(total_number_of_bookings=total_number_of_bookings,
                 average_length_of_stay=average_length_of_stay.__round__(2),
                 average_daily_rate=average_daily_rate.__round__(2),
                 number_of_cancelled_bookings=number_of_cancelled_bookings,
                 number_of_non_cancelled_bookings=number_of_non_cancelled_bookings,
                 the_most_popular_market_segment=the_most_popular_market_segment)
    ]


@router.get('/bookings/analysis',
            response_model=List[GetAnalysis],
            tags=['Main functionalities'],
            description='Endpoint performs advanced analysis on the dataset, generating insights and trends based on speci'
                        'fic criteria, such as booking trends by month, guest demographics, popular meal packages, etc.')
async def analysis_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[GetAnalysis]:
    most_popular_arrive_month = df['arrival_date_month'].value_counts().index[0]
    least_popular_arrive_month = df['arrival_date_month'].value_counts().index[11]

    df['arrive_date'] = pd.to_datetime(df['arrival_date_year'].astype(str) + '-' + df['arrival_date_month'] + '-' + df[
        'arrival_date_day_of_month'].astype(str))
    df['booking_date_month'] = (df['arrive_date'] - pd.to_timedelta(df['lead_time'], unit='D')).dt.month_name()
    most_popular_booking_month = df['booking_date_month'].value_counts().index[0]
    least_popular_booking_month = df['booking_date_month'].value_counts().index[11]

    all_guest_without_children = len(df[(df['is_canceled'] == 0) & (df['babies'] == 0) & (df['children'] == 0.0)])
    all_guest_with_children_or_babyes = len(
        df[(df['is_canceled'] == 0) & ((df['babies'] > 0) | (df['children'] > 0.0))])
    lonely_guest = len(
        df[(df['is_canceled'] == 0) & (df['adults'] == 1) & (df['babies'] == 0) & (df['children'] == 0.0)])
    couple_without_children_and_babyes = len(
        df[(df['is_canceled'] == 0) & (df['adults'] == 2) & (df['babies'] == 0) & (df['children'] == 0.0)])

    df['revenue'] = (df['stays_in_weekend_nights'] + df['stays_in_week_nights']) * df['adr']
    percentage_of_people_with_a_parking_space = (
            len(df[df['required_car_parking_spaces'] > 0]) / len(df) * 100).__round__(2)
    countries_by_order = df['country'].value_counts().head().to_dict()
    meal_packages = df['meal'].value_counts().to_dict()
    return [
        GetAnalysis(most_popular_arrive_month=most_popular_arrive_month,
                    least_popular_arrive_month=least_popular_arrive_month,
                    most_popular_booking_month=most_popular_booking_month,
                    least_popular_booking_month=least_popular_booking_month,
                    all_guest_without_children=all_guest_without_children,
                    all_guest_with_children_or_babyes=all_guest_with_children_or_babyes,
                    couple_without_children_and_babyes=couple_without_children_and_babyes,
                    lonely_guest=lonely_guest,
                    percentage_of_people_with_a_parking_space=percentage_of_people_with_a_parking_space,
                    most_popular_countries_by_order=countries_by_order,
                    meal_packages=meal_packages)
    ]


@router.get('/bookings/nationality',
            response_model=List[AllBookings],
            tags=['Advanced functionalities'],
            description='Endpoint retrieves bookings based on the provided nationality. (Categories are represented in '
                        'the ISO 3155–3:2013 format)')
async def nationality_bookings(country: Annotated[str, Query(min_length=2, max_length=3)],
                               df: DataFrame = Depends(read_csv_bookings)) -> List[AllBookings]:
    df = df.fillna(value=0)

    if country is None:
        raise HTTPException(status_code=400, detail="Country parameter is required")

    if not country.isalpha():
        raise HTTPException(status_code=400, detail="Country must contain only letters")
    result = df[df['country'] == country.upper()].rename(columns={'phone-number': 'phone_number'}).head(5)
    if result.empty:
        raise HTTPException(status_code=404, detail="No bookings found for provided country")

    return [
        AllBookings(hotel=row.hotel,
                    is_canceled=row.is_canceled,
                    lead_time=row.lead_time,
                    arrival_date_year=row.arrival_date_year,
                    arrival_date_month=row.arrival_date_month,
                    arrival_date_week_number=row.arrival_date_week_number,
                    arrival_date_day_of_month=row.arrival_date_day_of_month,
                    stays_in_weekend_nights=row.stays_in_weekend_nights,
                    stays_in_week_nights=row.stays_in_week_nights,
                    adults=row.adults, children=row.children, babies=row.babies, meal=row.meal, country=row.country,
                    market_segment=row.market_segment, distribution_channel=row.distribution_channel,
                    is_repeated_guest=row.is_repeated_guest, previous_cancellations=row.previous_cancellations,
                    previous_bookings_not_canceled=row.previous_bookings_not_canceled,
                    reserved_room_type=row.reserved_room_type, assigned_room_type=row.assigned_room_type,
                    booking_changes=row.booking_changes, deposit_type=row.deposit_type, agent=row.agent,
                    company=row.company, days_in_waiting_list=row.days_in_waiting_list, customer_type=row.customer_type,
                    adr=row.adr, required_car_parking_spaces=row.required_car_parking_spaces,
                    total_of_special_requests=row.total_of_special_requests, reservation_status=row.reservation_status,
                    reservation_status_date=row.reservation_status_date, name=row.name, email=row.email,
                    phone_number=row.phone_number, credit_card=row.credit_card)
        for row in result.itertuples(index=False)
    ]


@router.get('/bookings/popular_meal_package',
            response_model=List[PopularMealPackage],
            tags=['Advanced functionalities'],
            description='Endpoint retrieves the most popular meal package.')
async def popular_meal_package_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[PopularMealPackage]:
    result = df['meal'].value_counts().index[0]
    return [
        PopularMealPackage(the_most_popular_meal_package=result)
    ]


@router.get('/bookings/avg_length_of_stay',
            response_model=List[AvgLengthOfStay],
            tags=['Advanced functionalities'],
            description='Endpoint retrieves the average length of stay for each combination of booking year and hotel type.')
async def avg_length_of_stay_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[AvgLengthOfStay]:
    df['avg_length_of_stay'] = df['stays_in_weekend_nights'] + df['stays_in_week_nights']
    df['arrive_date'] = pd.to_datetime(df['arrival_date_year'].astype(str) + '-' + df['arrival_date_month'] + '-' + df[
        'arrival_date_day_of_month'].astype(str))
    df['booking_date_year'] = (df['arrive_date'] - pd.to_timedelta(df['lead_time'], unit='D')).dt.year
    result = df[df['is_canceled'] == 0].groupby(['booking_date_year', 'hotel'])['avg_length_of_stay'].mean().round(
        2).reset_index(name='avg_length_of_stay')
    return [
        AvgLengthOfStay(year=row.booking_date_year, hotel=row.hotel, avg_length_of_stay=row.avg_length_of_stay)
        for row in result.itertuples(index=False)
    ]


@router.get('/bookings/total_revenue',
            response_model=List[TotalRevenue],
            tags=['Advanced functionalities'],
            description='Endpoint retrieves the total revenue for each combination of booking month and hotel type.')
async def total_revenue_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[TotalRevenue]:
    df['revenue'] = (df['stays_in_weekend_nights'] + df['stays_in_week_nights']) * df['adr']
    df['arrive_date'] = pd.to_datetime(df['arrival_date_year'].astype(str) + '-' + df['arrival_date_month'] + '-' + df[
        'arrival_date_day_of_month'].astype(str))
    df['booking_date_month'] = (df['arrive_date'] - pd.to_timedelta(df['lead_time'], unit='D')).dt.month_name()

    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']

    df['booking_date_month'] = pd.Categorical(df['booking_date_month'], categories=month_order, ordered=True)

    result = df[df['is_canceled'] == 0].groupby(['booking_date_month', 'hotel'], observed=True)[
        'revenue'].sum().reset_index(name='total_revenue')

    return [
        TotalRevenue(month=row.booking_date_month, hotel=row.hotel, total_revenue=row.total_revenue)
        for row in result.itertuples(index=False)
    ]


@router.get('/bookings/top_countries',
            response_model=List[Country],
            tags=['Advanced functionalities'],
            description='Endpoint retrieves the top 5 countries with the most bookings.')
async def top_countries_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[Country]:
    result = df[df['is_canceled'] == 0]['country'].value_counts().head(5).reset_index(name='counts')
    return [
        Country(country=row.country, count_of_bookings=row.counts)
        for row in result.itertuples(index=False)
    ]


@router.get('/bookings/repeated_guests_percentage',
            response_model=List[RepGuestPrecent],
            tags=['Advanced functionalities'],
            description='Endpoint retrieves the percentage of repeated guests.')
async def repeated_guests_percentage_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[RepGuestPrecent]:
    result = (df['is_repeated_guest'].sum() / len(df) * 100).__round__(2)
    return [
        RepGuestPrecent(repeated_guests_percentage=result)
    ]


@router.get('/bookings/total_guests_by_year',
            response_model=List[TotalGuestByYear],
            tags=['Advanced functionalities'],
            description='Endpoint retrieves the total number of guests by booking year.')
async def total_guests_by_year_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[TotalGuestByYear]:
    df['arrive_date'] = pd.to_datetime(df['arrival_date_year'].astype(str) + '-' + df['arrival_date_month'] + '-' + df[
        'arrival_date_day_of_month'].astype(str))
    df['booking_date_year'] = (df['arrive_date'] - pd.to_timedelta(df['lead_time'], unit='D')).dt.year
    df['total_guest'] = df['adults'] + df['children'] + df['babies']
    result = df[df['is_canceled'] == 0].groupby(['booking_date_year'])['total_guest'].sum().reset_index(
        name='count_guests')
    return [
        TotalGuestByYear(year=row.booking_date_year, count_guests=row.count_guests)
        for row in result.itertuples(index=False)
    ]


@router.get('/bookings/avg_daily_rate_resort',
            response_model=List[AvgDailyRateResort],
            tags=['Advanced functionalities'],
            dependencies=[Depends(verify_credentials)],
            description='Endpoint retrieves the average daily rate by month for resort hotel bookings.')
async def avg_daily_rate_resort_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[AvgDailyRateResort]:
    df['arrive_date'] = pd.to_datetime(df['arrival_date_year'].astype(str) + '-' + df['arrival_date_month'] + '-' + df[
        'arrival_date_day_of_month'].astype(str))
    df['booking_date_month'] = (df['arrive_date'] - pd.to_timedelta(df['lead_time'], unit='D')).dt.month_name()
    grouped = df[(df['hotel'] == 'Resort Hotel') & (df['is_canceled'] == 0)].groupby(['booking_date_month'])[
        'adr'].mean().__round__(2)

    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                   'November', 'December']
    result = grouped.reindex(sorted(grouped.index, key=month_order.index)).reset_index(name='avg_daily')
    return [
        AvgDailyRateResort(month=row.booking_date_month, avg_daily=row.avg_daily)
        for row in result.itertuples(index=False)
    ]


@router.get('/bookings/most_common_arrival_day_city',
            response_model=List[MostCommonArrivalDayCity],
            tags=['Advanced functionalities'],
            dependencies=[Depends(verify_credentials)],
            description='Endpoint retrieves the most common arrival date day of the week for city hotel bookings.')
async def most_common_arrival_day_city_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[
    MostCommonArrivalDayCity]:
    df['arrive_date'] = pd.to_datetime(df['arrival_date_year'].astype(str) + '-' + df['arrival_date_month'] + '-' + df[
        'arrival_date_day_of_month'].astype(str))
    df['most_common_arrival_day'] = to_datetime(df['arrive_date']).dt.day_name()
    result = (df[(df['hotel'] == 'City Hotel') & (df['is_canceled'] == 0)][
                  'most_common_arrival_day'].value_counts().sort_values(ascending=False).head(1)).reset_index(
        name='counts')
    return [
        MostCommonArrivalDayCity(day_of_the_week=row.most_common_arrival_day, counts_of_arrivals=row.counts)
        for row in result.itertuples(index=False)
    ]


@router.get('/bookings/count_by_hotel_meal',
            response_model=List[CountMeal],
            tags=['Advanced functionalities'],
            dependencies=[Depends(verify_credentials)],
            description='Endpoint retrieves the count of bookings by hotel type and meal package.')
async def count_by_hotel_meal_bookings(df: DataFrame = Depends(read_csv_bookings)) -> List[CountMeal]:
    result = df[df['is_canceled'] == 0].groupby(['meal', 'hotel']).size().reset_index(name='counts_meal')
    return [
        CountMeal(hotel=row.hotel, meal=row.meal, counts=row.counts_meal)
        for row in result.itertuples(index=False)
    ]


@router.get('/bookings/total_revenue_resort_by_country',
            response_model=List[TotalRevenueByCountry],
            tags=['Advanced functionalities'],
            dependencies=[Depends(verify_credentials)],
            description='Endpoint retrieves the total revenue by country for resort hotel bookings.')
async def total_revenue_resort_by_country_bookings(
        df: DataFrame = Depends(read_csv_bookings)) -> List[TotalRevenueByCountry]:
    df['revenue'] = (df['stays_in_weekend_nights'] + df['stays_in_week_nights']) * df['adr']
    revenue = df[(df['is_canceled'] == 0) & (df['hotel'] == 'Resort Hotel')].groupby(['country'])['revenue'].sum()
    result = revenue.sort_values(ascending=False).reset_index(name='total_revenue')
    return [
        TotalRevenueByCountry(country=row.country, total_revenue=row.total_revenue)
        for row in result.itertuples(index=False)
    ]


@router.get('/bookings/count_by_hotel_repeated_guest',
            response_model=List[RepeatGuest],
            tags=['Advanced functionalities'],
            dependencies=[Depends(verify_credentials)],
            description='Endpoint retrieves the count of bookings grouped by hotel type and repeated guest status.'
                        ' Returns: The count of bookings by hotel type and repeated guest status.')
async def count_by_hotel_repeated_guest_bookings(
        df: DataFrame = Depends(read_csv_bookings)) -> List[RepeatGuest]:
    repeat_guest = df[df['is_canceled'] == 0].groupby(['hotel', 'is_repeated_guest']).size().reset_index(
        name='counts')
    return [
        RepeatGuest(hotel=row.hotel, is_repeat=row.is_repeated_guest, count_guests=row.counts)
        for row in repeat_guest.itertuples(index=False)
    ]


@router.get('/bookings/{booking_id}',
            response_model=List[GetBookings],
            tags=['Main functionalities'],
            description='Endpoint retrieves details of a specific booking by its unique ID.')
async def get_bookings_id(booking_id: int,
                          db: Session = Depends(get_db)) -> List[GetBookings]:
    if not isinstance(booking_id, int):
        raise HTTPException(status_code=400, detail="booking_id must be an integer")

    try:
        # Checking the connection to the database
        db.execute(text("SELECT 1"))
    except OperationalError:
        raise HTTPException(status_code=500, detail="Database connection error")

    result = db.scalars(select(Bookings).where(Bookings.id == booking_id)).first()

    if not result:
        raise HTTPException(status_code=404, detail="Booking not found")

    return [GetBookings(**result.__dict__)]
