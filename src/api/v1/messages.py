from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query
from fastapi.responses import StreamingResponse
from prisma.models import Messages
from pydantic import ValidationError

from src.agents.agent_loader import agent_loader
from src.db.prisma import prisma
from src.models.messages import MessageContent, MessageCreateInput
from src.models.pagination import Pagination

router = APIRouter()


@router.get(
    "/v1/threads/{thread_id}/messages",
    tags=["messages"],
    response_model=Pagination[Messages],
    description="Retrieves all messages for a given thread. Returns a list of all messages by default in descending chronological order (newest first).",
)
async def get_messages(
    thread_id: str = Path(
        ...,
        description="The unique identifier of the thread. Can be either the internal ID or external ID.",
    ),
    limit: int = Query(default=10, ge=1),
    offset: int = Query(default=0, ge=0),
    order: Literal["asc", "desc"] = Query(default="desc"),
):
    messages = await prisma.messages.find_many(
        where={
            "OR": [
                {"thread_id": thread_id},
                {"thread": {"is": {"external_id": thread_id}}},
            ],
        },
        order=[{"created_at": order}],
        take=limit,
        skip=offset,
    )

    return Pagination(data=messages, limit=limit, offset=offset)


@router.post(
    "/v1/threads/{thread_id}/messages",
    tags=["messages"],
    response_model=MessageContent,
    response_description="A stream of JSON-encoded message chunks. See the `MessageContent` schema for the structure of the message chunks.",
)
async def create_message(
    message: MessageCreateInput,
    thread_id: str = Path(
        ...,
        description="The unique identifier of the thread. Can be either the internal ID or external ID.",
    ),
):
    thread = await prisma.threads.find_first(
        where={
            "OR": [
                {"id": thread_id},
                {"external_id": thread_id},
            ],
        },
    )

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    agent = agent_loader.get_agent(message.agent_config.agent_class)

    if not agent:
        raise HTTPException(
            status_code=404,
            detail=f"Agent '{message.agent_config.agent_class}' is not a valid agent. Available agents: {', '.join(map(lambda agent: agent.__class__.__name__, agent_loader.agents))}",
        )

    config = message.agent_config.model_dump()
    del config["agent_class"]

    async def stream(thread_id: str):
        chunks: list[MessageContent] = []
        for chunk in agent.forward(message.content[0].content, config):
            last_chunk = chunks[-1] if chunks else None

            if last_chunk and last_chunk.type == "text":
                last_chunk.content += chunk.content
            else:
                chunks.append(chunk)

            yield chunk.model_dump_json() + "\n"

        await prisma.messages.create(
            data={
                "thread": {"connect": {"id": thread_id}},
                "agent_class": message.agent_config.agent_class,
                "role": "user",
                "contents": {
                    "create": [
                        {
                            "content": content.content,
                            "message_type": content.type,
                        }
                        for content in message.content
                    ]
                },
            },
        )

        # Insert agent response
        await prisma.messages.create(
            data={
                "thread": {"connect": {"id": thread_id}},
                "agent_class": message.agent_config.agent_class,
                "role": "assistant",
                "contents": {
                    "create": [
                        {
                            "content": chunk.content,
                            "message_type": chunk.type,
                        }
                        for chunk in chunks
                    ],
                },
            },
        )

    try:
        return StreamingResponse(
            stream(thread.id),
            media_type="application/x-ndjson",
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/v1/threads/{thread_id}/messages/{message_id}",
    tags=["messages"],
)
async def delete_message(
    # TODO: Validate the user has permission to delete the message
    _: str = Path(
        ...,
        description="The unique identifier of the thread. Can be either the internal ID or external ID.",
    ),
    message_id: str = Path(..., description="The unique identifier of the message."),
):
    return await prisma.messages.delete(where={"id": message_id})