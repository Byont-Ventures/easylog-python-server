import inspect
import json
import os
from abc import abstractmethod
from typing import Any, AsyncGenerator, Generator, Generic, List, TypeVar, get_args

from prisma.models import Threads
from pydantic import BaseModel

from src.db.prisma import prisma
from src.logger import logger
from src.models.messages import Message, TextContent
from src.services.easylog_backend.backend_service import BackendService

TConfig = TypeVar("TConfig", bound=BaseModel)


class BaseAgent(Generic[TConfig]):
    """Base class for all agents."""

    thread_id: str
    _backend: BackendService | None = None
    _thread: Threads | None = None
    _raw_config: dict[str, Any] = {}

    _type_T: Any

    def __init__(self, thread_id: str, backend: BackendService | None = None, **kwargs):
        self.thread_id = thread_id
        self._backend = backend
        self._raw_config = kwargs

        logger.info(f"Initialized agent: {self.__class__.__name__}")

    def __init_subclass__(cls) -> None:
        cls._type_T = get_args(cls.__orig_bases__[0])[0]  # type: ignore

        logger.info(f"Initialized subclass: {cls.__name__}")

    @abstractmethod
    def on_message(self, messages: List[Message]) -> AsyncGenerator[TextContent, None]:
        raise NotImplementedError()

    def get_env(self, key: str) -> str:
        """A convenience method to get an environment variable."""

        env = os.getenv(key)

        if env is None:
            raise ValueError(
                f"Environment variable {key} is not found. Make sure .env file exists and {key} is set."
            )

        return env

    def forward(
        self,
        messages: List[Message],
    ) -> AsyncGenerator[TextContent, None]:
        """
        Forward the messages to the agent. Returns a generator of message contents.

        Args:
            messages: The messages to forward to the agent.

        Returns:
            A generator of messages.
        """

        logger.info(f"Forwarding message to agent: {self.__class__.__name__}")

        generator = self.on_message(messages)

        if not inspect.isasyncgen(generator):
            if inspect.isgenerator(generator):
                logger.warning(
                    "on_message returned a sync generator, converting to async generator"
                )
                generator = self._sync_to_async_generator(generator)
            else:
                raise ValueError(
                    "on_message must return either a sync or async generator"
                )

        return generator

    def get_metadata(self, key: str, default: Any = None) -> Any:
        metadata: dict = json.loads((self._get_thread()).metadata or "{}")

        return metadata.get(key, default)

    def set_metadata(self, key: str, value: Any) -> None:
        metadata: dict = json.loads((self._get_thread()).metadata or "{}")
        metadata[key] = value

        prisma.threads.update(
            where={"id": self.thread_id}, data={"metadata": json.dumps(metadata)}
        )

    @property
    def backend(self) -> BackendService:
        if self._backend is None:
            raise ValueError(
                "Backend is not initalized. This is usually because an authentication token wasn't provided in the request"
            )

        return self._backend

    @property
    def config(self) -> TConfig:
        return self._get_config(**self._raw_config)

    def _get_thread(self) -> Threads:
        """Get the thread for the agent."""

        if self._thread is None:
            self._thread = prisma.threads.find_first_or_raise(
                where={"id": self.thread_id}
            )

        return self._thread

    async def _sync_to_async_generator(self, sync_gen: Generator):
        for item in sync_gen:
            yield item

    def _get_config(self, **kwargs) -> TConfig:
        """Parse kwargs into the config type specified by the child class"""
        # Get the generic parameters using typing.get_args
        # Get the actual config type from the class's generic parameters

        if self._type_T:
            return self._type_T(**kwargs)

        raise ValueError("Could not determine config type from class definition")
