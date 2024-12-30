from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Request

async def get_database(request: Request):
    """Get database connection from request app state."""
    return request.app.mongodb
