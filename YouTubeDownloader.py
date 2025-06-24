from pytube import Playlist, YouTube
from pytube.cli import on_progress
import os


YouTube('https://youtu.be/2lAe1cqCOXo').streams.first().download()
yt = YouTube('http://youtube.com/watch?v=2lAe1cqCOXo')
yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()




from pprint import pprint
from fastapi import FastAPI, Path, Query, Body
import uvicorn


app = FastAPI()

hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Dubai", "name": "dubai"},
    {"id": 3, "title": "Moscow", "name": "moscow"}
]


@app.get("/hotels")
def get_hotels(
    id: int | None = Query(default=None, description="Идентификатор отеля"),
):
    if id:
        return [hotel for hotel in hotels if hotel["id"] == id]
    else:
        return hotels


@app.delete("/hotels/{hotel_id}")
def delete_hotel(hotel_id: int):
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotels.remove(hotel)
            return {"status": "OK"}
    return {"status": "ERROR"}


@app.post("/hotels")
def create_hotel(
        title: str = Body(embed=True, description="Название отеля"),
        name: str = Body(embed=True, description="Название отеля на английском"),
    ):
    hotels.append({
        "id": hotels[-1]["id"] + 1,
        "title": title,
        "name": name
    })
    return {"status": "OK"}


@app.put("/hotels/{hotel_id}")
def update_hotel(
        hotel_id: int = Path(embed=True, description="Идентификатор отеля"),
        title: str = Body(embed=True),
        name: str = Body(embed=True)
    ):
    """Меняет все параметры одного отеля"""
    for hotel in hotels:
        if hotel["id"] == hotel_id:
            hotel["title"] = title
            hotel["name"] = name
            return {"status": "OK"}
    return {"status": "ERROR. Hotel not found"}


@app.patch("/hotels/{hotel_id}")
def update_hotel(
        hotel_id: int = Path(embed=True, description="Идентификатор отеля"),
        title: str | None = Body(default=None, embed=True),
        name: str | None = Body(default=None, embed=True)
    ):
    """Меняет один из параметров или оба параметра одного отеля"""
    if title and name:
        for hotel in hotels:
            if hotel["id"] == hotel_id:
                hotel["title"] = title
                hotel["name"] = name
                return {"status": "OK"}
        return {"status": "ERROR. Hotel not found"}
    if title: 
        for hotel in hotels:
            if hotel["id"] == hotel_id:
                hotel["title"] = title
                return {"status": "OK"}
            return {"status": "ERROR(title). Hotel not found"}
    if name:
        for hotel in hotels:
            if hotel["id"] == hotel_id:
                hotel["name"] = name
                return {"status": "OK"}
            return {"status": "ERROR(name). Hotel not found"}
    return {"status": "ERROR. At least one parameter must be provided"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)