import json
from collections.abc import AsyncGenerator
from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query, Response, Security
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials
from prisma.models import messages

from src.lib.prisma import prisma
from src.logger import logger
from src.models.messages import MessageContent, MessageCreateInput
from src.models.pagination import Pagination
from src.security.optional_http_bearer import optional_bearer_header
from src.services.messages.message_service import MessageService
from src.utils.sse import create_sse_event

router = APIRouter()


@router.get(
    "/threads/{thread_id}/messages",
    name="get_messages",
    tags=["messages"],
    response_model=Pagination[messages],
    description="Retrieves all messages for a given thread. Returns a list of all messages by default in descending chronological order (newest first).",
)
async def get_messages(
    thread_id: str = Path(
        ...,
        description="The unique identifier of the thread. Can be either the internal ID or external ID.",
    ),
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    order: Literal["asc", "desc"] = Query(default="asc"),
) -> Pagination[messages]:
    messages = prisma.messages.find_many(
        where={
            "OR": [
                {"thread_id": thread_id},
                {"thread": {"is": {"external_id": thread_id}}},
            ],
        },
        order=[{"created_at": order}],
        include={"contents": True},
        take=limit,
        skip=offset,
    )

    return Pagination(data=messages, limit=limit, offset=offset)


@router.post(
    "/threads/{thread_id}/messages",
    name="create_message",
    tags=["messages"],
    response_model=MessageContent,
    response_description="A stream of JSON-encoded message chunks",
    description="Creates a new message in the given thread. Will interact with the agent and return a stream of message chunks.",
)
async def create_message(
    message: MessageCreateInput,
    thread_id: str = Path(
        ...,
        description="The unique identifier of the thread. Can be either the internal ID or external ID.",
    ),
    auth: HTTPAuthorizationCredentials | None = Security(optional_bearer_header),
) -> StreamingResponse:
    logger.info(f"Authorization: {auth}")

    thread = prisma.threads.find_first(
        where={
            "OR": [
                {"id": thread_id},
                {"external_id": thread_id},
            ],
        },
    )

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    agent_config = message.agent_config.model_dump()
    del agent_config["agent_class"]

    forward_message_generator = MessageService.forward_message(
        thread_id=thread.id,
        agent_class=message.agent_config.agent_class,
        agent_config=agent_config,
        input_content=list(message.content),
        bearer_token=auth.credentials if auth else None,
    )

    async def stream() -> AsyncGenerator[str, None]:
        try:
            async for chunk in forward_message_generator:
                sse_event = create_sse_event("delta", chunk.model_dump_json())
                logger.debug(f"Sending sse delta event to client: {sse_event}")
                yield sse_event
        except Exception as e:
            logger.exception("Error in SSE stream", exc_info=e)
            sse_event = create_sse_event("error", json.dumps({"detail": str(e)}))
            logger.warning(f"Sending sse error event to client: {sse_event}")
            yield sse_event

    return StreamingResponse(
        stream(),
        media_type="text/event-stream",
        headers={
            "Transfer-Encoding": "chunked",
            "X-Accel-Buffering": "no",
        },
    )


@router.delete(
    "/threads/{thread_id}/messages/{message_id}",
    tags=["messages"],
    name="delete_message",
)
async def delete_message(
    thread_id: str = Path(
        ...,
        description="The unique identifier of the thread. Can be either the internal ID or external ID.",
    ),
    message_id: str = Path(..., description="The unique identifier of the message."),
) -> Response:
    prisma.messages.delete_many(
        where={
            "AND": [
                {"id": message_id},
                {"thread_id": thread_id},
            ],
        }
    )

    return Response(status_code=204)
