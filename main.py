import uvicorn

from fastapi import FastAPI

from config import *
from db import database, models
from endpoints.endpoints import router
from endpoints.depends import create_db_data

# Set up the FastAPI application
app = FastAPI(
    title="Bookings App",
    description=API_DESCRIPTION,
    version=API_VERSION
)
app.include_router(router=router)

models.Base.metadata.create_all(bind=database.engine)

# Run the FastAPI aplication
if __name__ == '__main__':
    create_db_data()
    uvicorn.run("main:app", host=SERVER_HOST, port=SERVER_PORT, reload=True)
