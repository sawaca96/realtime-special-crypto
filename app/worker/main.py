from datetime import timedelta

import faust

# faust -A app.worker.main worker -l info


class Trade(faust.Record):
    code: str
    p: float
    v: float
    vv: float
    t: int


app = faust.App(
    "trade",
    broker="kafka://localhost:9091,kafka://localhost:9092,kafka://localhost:9093",
    topic_partitions=10,
    topic_replication_factor=3,
)


trade_views = app.Table("trade", default=int).tumbling(
    timedelta(minutes=1),
    expires=timedelta(minutes=30),
)

trade_topic = app.topic("trade", value_type=Trade)


@app.agent(trade_topic)
async def aggregate_trade_views(trades: faust.StreamT[Trade]) -> None:
    # values in this streams are URLs as strings.
    async for trade in trades:
        code = trade.code
        # increment one to all windows this page URL fall into.
        trade_views[code] += 1

        if trade_views[code].now() >= 10000:
            # Page is trending for current processing time window
            print("Trending now")

        if trade_views[code].current() >= 10000:
            # Page would be trending in the current event's time window
            print("Trending when event happened")

        if trade_views[code].value() >= 10000:
            # Page would be trending in the current event's time window
            # according to the relative time set when creating the
            # table.
            print("Trending when event happened")

        if trade_views[code].delta(timedelta(minutes=1)) > trade_views[code].now():
            print("Less popular compared to 1 minutes back")
