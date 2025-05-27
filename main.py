from fastapi import FastAPI, HTTPException
from models import Book, UpdateBookDTO
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

mongo_url = os.getenv("MONGO_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):
    await startup_db_client(app)
    yield
    await shutdown_db_client(app)

async def startup_db_client(app):
    app.mongodb_client = AsyncIOMotorClient(mongo_url)
    app.mongodb = app.mongodb_client.get_database("library")

    # Crear índices para búsquedas eficientes
    #await app.mongodb["books"].create_index("title")
    #await app.mongodb["books"].create_index("author")
    #await app.mongodb["books"].create_index("isbn", unique=True)

    print("MongoDB connected.")

async def shutdown_db_client(app):
    app.mongodb_client.close()
    print("Database disconnected.")

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library API"}

@app.post("/api/v1/create-book", response_model=Book)
async def create_book(book: Book):
    result = await app.mongodb["books"].insert_one(book.dict())
    inserted_book = await app.mongodb["books"].find_one({"_id": result.inserted_id})
    inserted_book.pop("_id")
    return inserted_book

@app.get("/api/v1/list-books", response_model=List[Book])
async def list_books():
    books = await app.mongodb["books"].find().to_list(None)
    for book in books:
        book.pop("_id", None)
    return books

@app.get("/api/v1/get-book/{isbn}", response_model=Book)
async def get_book(isbn: str):
    book = await app.mongodb["books"].find_one({"isbn": isbn})
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    book.pop("_id", None)
    return book

@app.put("/api/v1/update-book/{isbn}", response_model=Book)
async def update_book(isbn: str, book_update: UpdateBookDTO):
    updated_result = await app.mongodb["books"].update_one(
        {"isbn": isbn}, {"$set": book_update.dict(exclude_unset=True)}
    )
    if updated_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Book not found or no update needed")
    updated_book = await app.mongodb["books"].find_one({"isbn": isbn})
    updated_book.pop("_id", None)
    return updated_book

@app.delete("/api/v1/delete-book/{isbn}", response_model=dict)
async def delete_book(isbn: str):
    delete_result = await app.mongodb["books"].delete_one({"isbn": isbn})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Book not found")
    return {"message": "Book deleted successfully"}

@app.get("/api/v1/books/stats")
async def book_statistics():
    pipeline = [
        {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}}
    ]
    stats = await app.mongodb["books"].aggregate(pipeline).to_list(None)
    return stats
