from dotenv import load_dotenv
import os

load_dotenv()

DB_HOST = os.environ.get("DB_HOST")
AUTH_LOGIN = os.environ.get("AUTH_LOGIN")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD")
DB_PORT = os.environ.get("DB_PORT")
DB_URI = os.environ.get("DB_URI")
SERVER_HOST = os.environ.get("SERVER_HOST")
SERVER_PORT = int(os.environ.get("SERVER_PORT"))
API_DESCRIPTION = os.environ.get("API_DESCRIPTION")
API_VERSION = os.environ.get("API_VERSION")
