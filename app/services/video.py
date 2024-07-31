from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from app.config import mongo_url
from typing import List

client = AsyncIOMotorClient(mongo_url)
db = client.videos
videos_collection = db.videos

async def save_video_metadata(video_data: dict):
    result = await videos_collection.insert_one(video_data)
    return str(result.inserted_id)

async def get_video_by_id(video_id: str):
    video = await videos_collection.find_one({"_id": ObjectId(video_id)})
    return video

async def update_video_metadata(video_id: str, metadata: dict):
    result = await videos_collection.update_one(
        {"_id": ObjectId(video_id)},
        {"$set": metadata}
    )
    return result.matched_count

async def delete_video_by_id(video_id: str):
    result = await videos_collection.delete_one({"_id": ObjectId(video_id)})
    return result.deleted_count
