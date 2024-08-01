from fastapi import FastAPI
from app.routers import video

app = FastAPI(   
    title="Video Management API",
    description="A FastAPI-based Video Management API for uploading, downloading, updating, and deleting videos with metadata handling and tag support.",
    version="1.0.0",
    terms_of_service="http://foo.com",
    contact={
        "name": "Support Team",
        "url": "http://fooo.com/contact",
        "email": "sahilk@gmail.com",
    },
    license_info={
        "name": "Lisence 1.0.0",
        "url": "https://www.fooo.com/licenses",
    },
    servers=[
        {
            "url": "http://127.0.0.1:8000",
            # "description": "Local Server"
        }
    ]
    )

app.include_router(video.router)
