import asyncio
import uuid
from typing import TypedDict

import orjson
from websockets.client import connect
from websockets.exceptions import ConnectionClosed

from app.producer import AIOProducer

#  python app/trade/main.py

UPBIT_WS_URI = "wss://api.upbit.com/websocket/v1"


class Trade(TypedDict):
    code: str
    p: float
    v: float
    vv: float
    t: int


class UpbitSocket:
    def __init__(self) -> None:
        self._producer = AIOProducer(
            {
                "bootstrap.servers": "localhost:9091,localhost:9092,localhost:9093",
                "acks": "1",
            }
        )

    async def connect(self) -> None:
        self._producer.start()
        self._ws = await connect(UPBIT_WS_URI, ping_interval=10)
        message = [
            {"ticket": str(uuid.uuid4())},
            {
                "type": "trade",
                "codes": [
                    "KRW-BTC",
                    "KRW-ETH",
                    "KRW-RFR",
                    "KRW-SUI",
                    "KRW-CTC",
                    "KRW-MINA",
                    "KRW-IMX",
                    "KRW-SEI",
                    "KRW-EGLD",
                    "KRW-NU",
                    "KRW-ASTR",
                    "KRW-GRS",
                    "KRW-TRX",
                    "KRW-BLUR",
                    "KRW-GRT",
                    "KRW-WEMIX",
                    "KRW-PLA",
                    "KRW-NEO",
                    "KRW-HPO",
                    "KRW-ZIL",
                    "KRW-KNC",
                    "KRW-MANA",
                    "KRW-IQ",
                    "KRW-MATIC",
                    "KRW-HUM",
                    "KRW-THETA",
                    "KRW-ETH",
                    "KRW-FLOW",
                    "KRW-CBK",
                    "KRW-APT",
                    "KRW-XRP",
                    "KRW-MTL",
                    "KRW-CRO",
                    "KRW-POLYX",
                    "KRW-KAVA",
                    "KRW-T",
                    "KRW-MED",
                    "KRW-REP",
                    "KRW-TON",
                    "KRW-MOC",
                    "KRW-SBD",
                    "KRW-OMG",
                    "KRW-IOTA",
                    "KRW-JST",
                    "KRW-STMX",
                    "KRW-MBL",
                    "KRW-HBAR",
                    "KRW-ZRX",
                    "KRW-SRM",
                    "KRW-ARB",
                    "KRW-TT",
                    "KRW-WAVES",
                ],
                "isOnlyRealtime": True,
            },
            {"format": "SIMPLE"},
        ]
        await self._ws.send(orjson.dumps(message))

    async def publish_trade(self) -> None:
        while True:
            message = await self._ws.recv()
            data = orjson.loads(message)
            code = data["cd"]
            trade = Trade(
                code=code,
                p=float(data["tp"]),
                v=float(data["tv"]),
                vv=float(data["tp"]) * float(data["tv"]),
                t=int(data["ttms"]),
            )
            self._producer.produce(
                "trade", orjson.dumps(trade), key=f"code:{code}".encode()
            )

    async def disconnect(self) -> None:
        try:
            await self._ws.close()
        except ConnectionClosed:
            pass


async def main() -> None:
    socket = UpbitSocket()
    await socket.connect()
    await socket.publish_trade()


if __name__ == "__main__":
    asyncio.run(main())
