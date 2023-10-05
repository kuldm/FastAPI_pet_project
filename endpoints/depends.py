import pandas as pd

from sqlalchemy import create_engine


async def read_csv_bookings():
    df = pd.read_csv('hotel_booking_data.csv')
    return df


def create_db_data():
    df = pd.read_csv('hotel_booking_data.csv')

    df['guest_name'] = df['name']
    df['daily_rate'] = df['adr']
    df['length_of_stay'] = df['stays_in_weekend_nights'].astype(int) + df['stays_in_week_nights'].astype(int)
    df['arrive_date'] = pd.to_datetime(
        df['arrival_date_year'].astype(str) + '-' + df['arrival_date_month'].astype(str) + '-' + df[
            'arrival_date_day_of_month'].astype(
            str))
    df['booking_date'] = df['arrive_date'].dt.date - pd.to_timedelta(df['lead_time'], unit='day')

    df['id'] = df.index

    df = df[['id', 'booking_date', 'length_of_stay', 'guest_name', 'daily_rate']]

    engine = create_engine('sqlite:///hotel.db', echo=True)

    df.to_sql('bookings', con=engine, if_exists='replace', index=False)
