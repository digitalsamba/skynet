from fastapi import APIRouter, Request
import httpx
from skynet.utils import get_router

openai_router = get_router()  # Uses JWT authentication & error responses

OPENAI_API_BASE = "http://skynet-prod:8003/v1"  # Change if using a local server

@openai_router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_openai_request(path: str, request: Request):
    async with httpx.AsyncClient() as client:
        response = await client.request(
            request.method,
            f"{OPENAI_API_BASE}/{path}",
            headers=dict(request.headers),
            content=await request.body()
        )
    return response.json()