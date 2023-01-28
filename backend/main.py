from typing import Union
from fastapi import FastAPI
import motor.motor_asyncio


client = MongoClient('mongodb://localhost:27017/')
db = client.animedb
app = FastAPI()


@app.get("/animes", )
def read_root(q: Union[str, None] = None):
    return {"Hello": "World", "q": q}


@app.get("/animes/{anime_slug}")
def read_item(anime_slug: str):
    return db.animes.get_one(filter={'slug': anime_slug})