import uvicorn
from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from skynet.auth.bearer import JWTBearer
from skynet.env import (
    bypass_auth,
    listen_ip,
    ws_max_ping_interval,
    ws_max_ping_timeout,
    ws_max_queue_size,
    ws_max_size_bytes,
)
from skynet.logs import get_logger, uvicorn_log_config

log = get_logger(__name__)


def create_app(**kwargs):
    app = FastAPI(**kwargs)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


dependencies = [] if bypass_auth else [Depends(JWTBearer())]
responses = (
    {}
    if bypass_auth
    else {401: {"description": "Invalid or expired token"}, 403: {"description": "Not enough permissions"}}
)


def get_router() -> APIRouter:
    return APIRouter(dependencies=dependencies, responses=responses)


async def create_webserver(app, port):
    server_config = uvicorn.Config(
        app,
        host=listen_ip,
        port=port,
        log_config=uvicorn_log_config,
        ws_max_size=ws_max_size_bytes,
        ws_ping_interval=ws_max_ping_interval,
        ws_ping_timeout=ws_max_ping_timeout,
        ws_max_queue=ws_max_queue_size,
    )
    server = uvicorn.Server(server_config)
    await server.serve()


def get_customer_id(request: Request) -> str:
    id = request.query_params.get("customerId")

    if not id:
        id = request.state.decoded_jwt.get("cid") if hasattr(request.state, 'decoded_jwt') else None

    return id


def get_app_id(request: Request) -> str:
    return request.state.decoded_jwt.get('appId') if hasattr(request.state, 'decoded_jwt') else None
