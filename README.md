## Hotel Booking Analysis API
==========================

Version: 1.0


## Description:
---------------
The Hotel Booking Analysis API aims to provide a comprehensive set of endpoints 
for analyzing and retrieving insights from a dataset containing booking information
for a city hotel and a resort hotel. With using with Python, Fast Api, SQLite, 
SQLAlchemy, Pandas and Pedantic.


## Features:
------------
- [x] Database Connection Using SQLAlchemy
- [x] FastAPI Server
- [x] HTTPBasicCredentials and HTTP basic authentication
- [x] Pandas DataFrame


## Dependencies
---------------
- Python 3.11
- Pip
- Other listed in requirements.txt


## Database: hotel.db
------------
#### Table: bookings

Description: 
This table stores information about bookings at your hotel. 
Each entry in this table represents one booking with different characteristics.

Fields:
- 'id': The data type is an integer, the primary key. The unique identifier of each booking.
- 'booking_date': Typical booking date. Date of booking.
- 'length_of_stay': The data type is an integer. Duration of stay (number of nights).
- 'user_name': The data type is a string. The name of the guest who made the reservation.
- 'daily_rate': The data type is floating. The daily rate for accommodation.

Sample recording:
- 'id': 1
- 'booking_date': "2013-06-24"
- 'length_of_stay': 0
- 'user_name': "Andrea Baker"
- 'daily_rate': 0


## Running:
-----------
- Create a Virtual Environment
- Activate the virtualenv
- Install dependencies from requirements.txt
- To run the main.py


## Author(s) and contacts:
-------------------------
Developer: Kultyshev Dmitriy
Email: prizrak2165@gmail.com
GitHub: https://github.com/kuldm
