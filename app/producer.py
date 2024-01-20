import asyncio
from collections.abc import Callable
from threading import Thread
from typing import Any, Protocol

from confluent_kafka import KafkaException, Producer


class Message(Protocol):
    def error(self) -> str:
        pass

    def key(self) -> bytes:
        pass

    def latency(self) -> float:
        pass

    def offset(self) -> int:
        pass

    def partition(self) -> int:
        pass

    def timestamp(self) -> tuple[int, int]:
        pass

    def topic(self) -> str:
        pass

    def value(self) -> bytes:
        pass


class AIOProducer:
    def __init__(
        self, configs: dict[str, Any], loop: asyncio.AbstractEventLoop | None = None
    ) -> None:
        self._loop = loop or asyncio.get_event_loop()
        self._configs = configs
        self._cancelled = False
        self._poll_thread: Thread | None = None
        self._producer: Producer | None = None

    def _poll_loop(self) -> None:
        while not self._cancelled:
            self._producer.poll(0.1)

    def start(self) -> None:
        self._producer = Producer(self._configs)
        self._poll_thread = Thread(target=self._poll_loop)
        self._poll_thread.start()

    def close(self) -> None:
        self._cancelled = True
        self._poll_thread.join()

    def produce(
        self,
        topic: str,
        value: str | bytes,
        key: str | bytes | None = None,
        on_delivery: Callable[[str, Message], None] = None,
    ) -> Any | asyncio.Future[Any]:
        result = self._loop.create_future()

        def ack(err: str, msg: Message) -> None:
            if err:
                self._loop.call_soon_threadsafe(
                    result.set_exception, KafkaException(err)
                )
            else:
                self._loop.call_soon_threadsafe(result.set_result, msg)
            if on_delivery:
                self._loop.call_soon_threadsafe(on_delivery, err, msg)

        self._producer.produce(topic, value, key=key, on_delivery=ack)
        return result
