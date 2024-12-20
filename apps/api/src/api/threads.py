from typing import Literal

from fastapi import APIRouter, HTTPException, Path, Query
from prisma.models import Threads

from src.db.prisma import prisma
from src.models.pagination import Pagination
from src.models.threads import ThreadCreateInput

router = APIRouter()


@router.get(
    "/threads",
    name="get_threads",
    tags=["threads"],
    response_model=Pagination[Threads],
    description="Retrieves all threads. Returns a list of all threads with their messages by default in descending chronological order (newest first). Each message includes its full content.",
)
async def get_threads(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
    offset: int = Query(default=0, ge=0),
    order: Literal["asc", "desc"] = Query(default="desc"),
):
    threads = prisma.threads.find_many(
        take=limit,
        skip=offset,
        order={"created_at": order},
        include={
            "messages": {
                "order_by": {"created_at": order},
                "include": {
                    "contents": True,
                },
            }
        },
    )

    return Pagination(data=threads, limit=limit, offset=offset)


@router.get(
    "/threads/{id}",
    name="get_thread_by_id",
    tags=["threads"],
    response_model=Threads,
    responses={
        404: {"description": "Thread not found"},
    },
    description="Retrieves a specific thread by its unique ID. Returns the thread details along with its messages in descending chronological order (newest first). Each message includes its full content.",
)
async def get_thread_by_id(
    id: str = Path(
        ...,
        description="The unique identifier of the thread. Can be either the internal ID or external ID.",
    ),
):
    thread = prisma.threads.find_first(
        where={
            "OR": [
                {"id": id},
                {"external_id": id},
            ]
        },
        include={
            "messages": {
                "order_by": {"created_at": "desc"},
                "include": {
                    "contents": True,
                },
            }
        },
    )

    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    return thread


@router.post(
    "/threads",
    name="create_thread",
    tags=["threads"],
    response_model=Threads,
    description="Creates a new thread or returns the existing thread if it already exists.",
)
async def create_thread(thread: ThreadCreateInput):
    if thread.external_id:
        return prisma.threads.upsert(
            where={
                "external_id": thread.external_id,
            },
            data={
                "create": {
                    "external_id": thread.external_id,
                },
                "update": {},
            },
            include={
                "messages": {
                    "include": {
                        "contents": True,
                    },
                }
            },
        )

    return prisma.threads.create(
        data={"external_id": thread.external_id},
        include={
            "messages": {
                "include": {
                    "contents": True,
                },
            }
        },
    )


@router.delete(
    "/threads/{id}",
    name="delete_thread",
    tags=["threads"],
    description="Deletes a thread by its internal or external ID.",
)
async def delete_thread(
    id: str = Path(
        ...,
        description="The unique identifier of the thread. Can be either the internal ID or external ID.",
    ),
):
    return prisma.threads.delete_many(
        where={
            "OR": [
                {"id": id},
                {"external_id": id},
            ]
        }
    )
