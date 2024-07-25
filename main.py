from fastapi import FastAPI,File
from routes import f_router


app = FastAPI()

app.include_router(f_router.router)


