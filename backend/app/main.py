from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routes import cafes, areas

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CaféPick API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cafes.router, prefix="/api")
app.include_router(areas.router, prefix="/api")


@app.get("/")
def root():
    return {"message": "CaféPick API is running"}
