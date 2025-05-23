from datetime import timedelta
from enum import StrEnum
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field, TypeAdapter

from ..config import settings
from .score_model import ScoreAgg


class SortingOrder(StrEnum):
    SCORE = 'score'
    POPULAR = 'popular'
    RECENT = 'recent'
    TIME_BUCKET = 'time_bucket'
    HOUR = 'hour'
    DAY = 'day'
    REACTIONS = 'reactions'
    BALANCE = 'balance'


class ChannelTimeframe(StrEnum):
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'


PARENT_CASTS_AGE = {
    ChannelTimeframe.DAY: '1 day',
    ChannelTimeframe.WEEK: '7 days',
    ChannelTimeframe.MONTH: '30 days',
}


class CastsTimeframe(StrEnum):
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    THREE_MONTHS = 'three_months'
    SIX_MONTHS = 'six_months'


CASTS_AGE = {
    CastsTimeframe.DAY: '1 day',
    CastsTimeframe.WEEK: '1 week',
    CastsTimeframe.MONTH: '1 month',
    CastsTimeframe.THREE_MONTHS: '3 months',
    CastsTimeframe.SIX_MONTHS: '6 months',
}

CASTS_AGE_TD = {
    CastsTimeframe.DAY: timedelta(days=1),
    CastsTimeframe.WEEK: timedelta(days=7),
    CastsTimeframe.MONTH: timedelta(days=30),
    CastsTimeframe.THREE_MONTHS: timedelta(days=91),
    CastsTimeframe.SIX_MONTHS: timedelta(days=183),
}


class CastsTimeDecay(StrEnum):
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'
    NEVER = 'never'

    @property
    def timedelta(self) -> timedelta:
        try:
            return CastsTimeDecay._TIMEDELTAS[self]
        except KeyError:
            raise ValueError("{self!r} has no equivalent timedelta")


CastsTimeDecay._TIMEDELTAS = {
    CastsTimeDecay.MINUTE: timedelta(minutes=1),
    CastsTimeDecay.HOUR: timedelta(hours=1),
    CastsTimeDecay.DAY: timedelta(days=1),
}


class TrendingFeed(BaseModel):
    feed_type: Annotated[Literal['trending'], Field(alias="feedType")]
    lookback: CastsTimeframe = CastsTimeframe.WEEK
    agg: ScoreAgg = ScoreAgg.SUM
    score_threshold: Annotated[float, Field(alias="scoreThreshold", ge=0.0)] = (
        0.000000001
    )
    reactions_threshold: Annotated[int, Field(alias="reactionsThreshold", ge=0)] = 1
    cutoff_ptile: Annotated[int, Field(alias="cutoffPtile", le=100, ge=0)] = 100
    weights: str = 'L1C0R1Y1'
    sorting_order: Annotated[SortingOrder, Field(alias="sortingOrder")] = (
        SortingOrder.DAY
    )
    time_decay: Annotated[CastsTimeDecay, Field(alias="timeDecay")] = (
        CastsTimeDecay.HOUR
    )
    normalize: bool = True
    shuffle: bool = False
    timeout_secs: Annotated[int, Field(alias="timeoutSecs", ge=3, le=30)] = (
        settings.FEED_TIMEOUT_SECS
    )
    session_id: Annotated[str, Field(alias="sessionId")] = None
    channels: Annotated[list[str], Field(alias="channels")] = None


class PopularFeed(BaseModel):
    feed_type: Annotated[Literal['popular'], Field(alias="feedType")]
    lookback: CastsTimeframe = CastsTimeframe.WEEK
    agg: ScoreAgg = ScoreAgg.SUM
    score_threshold: Annotated[float, Field(alias="scoreThreshold", ge=0.0)] = (
        0.000000001
    )
    reactions_threshold: Annotated[int, Field(alias="reactionsThreshold", ge=0)] = 10
    weights: str = 'L1C1R1Y1'
    sorting_order: Annotated[SortingOrder, Field(alias="sortingOrder")] = (
        SortingOrder.SCORE
    )
    time_decay: Annotated[CastsTimeDecay, Field(alias="timeDecay")] = (
        CastsTimeDecay.NEVER
    )
    normalize: bool = True
    timeout_secs: Annotated[int, Field(alias="timeoutSecs", ge=3, le=30)] = (
        settings.FEED_TIMEOUT_SECS
    )
    session_id: Annotated[str, Field(alias="sessionId")] = None
    channels: Annotated[list[str], Field(alias="channels")] = None


class FarconFeed(BaseModel):
    feed_type: Annotated[Literal['farcon'], Field(alias="feedType")]
    lookback: CastsTimeframe = CastsTimeframe.WEEK
    agg: ScoreAgg = ScoreAgg.SUM
    score_threshold: Annotated[float, Field(alias="scoreThreshold", ge=0.0)] = 0.0
    reactions_threshold: Annotated[int, Field(alias="reactionsThreshold", ge=0)] = 1
    cutoff_ptile: Annotated[int, Field(alias="cutoffPtile", le=100, ge=0)] = 100
    weights: str = 'L1C1R1Y1'
    sorting_order: Annotated[SortingOrder, Field(alias="sortingOrder")] = (
        SortingOrder.HOUR
    )  # for fresher posts made during the day
    time_decay: Annotated[CastsTimeDecay, Field(alias="timeDecay")] = (
        CastsTimeDecay.HOUR
    )
    normalize: bool = True
    shuffle: bool = False
    timeout_secs: Annotated[int, Field(alias="timeoutSecs", ge=3, le=30)] = (
        settings.FEED_TIMEOUT_SECS
    )
    session_id: Annotated[str, Field(alias="sessionId")] = None
    channels: Annotated[list[str], Field(alias="channels")] = ["farcon", "farcon-nyc"]


class TokenFeed(BaseModel):
    feed_type: Annotated[Literal['token'], Field(alias="feedType")]
    token_address: Annotated[str, Field(alias="tokenAddress")]
    lookback: timedelta = timedelta(days=3)
    agg: ScoreAgg = ScoreAgg.SUMCUBEROOT
    score_threshold: Annotated[float, Field(alias="scoreThreshold", ge=0.0)] = 0.9
    reactions_threshold: Annotated[int, Field(alias="reactionsThreshold", ge=0)] = 1
    cutoff_ptile: Annotated[int, Field(alias="cutoffPtile", le=100, ge=0)] = 100
    weights: str = 'L1C1R1Y1'
    sorting_order: Annotated[SortingOrder, Field(alias="sortingOrder")] = (
        SortingOrder.DAY
    )
    time_bucket_length: Annotated[timedelta, Field(alias="timeBucketLength")] = (
        timedelta(hours=8)
    )
    limit_casts: Annotated[
        int | None,
        Field(
            alias="limitCasts",
            description="limit number of casts per caster per time bucket; None/null (default) = unlimited",
        ),
    ] = None
    # time decay default: depreciates 10% every day, compounded, 7-day cliff
    # days          1   2   3   4   5   6   7 ->cliff
    # strength (%)  90  81  73  66  59  53  48->0
    time_decay_base: Annotated[float, Field(alias="timeDecayBase", gt=0, le=0)] = 0.9
    time_decay_period: Annotated[timedelta, Field(alias="timeDecayPeriod")] = timedelta(
        days=1
    )
    normalize: bool = True
    shuffle: bool = False
    timeout_secs: Annotated[int, Field(alias="timeoutSecs", ge=3, le=30)] = (
        settings.FEED_TIMEOUT_SECS
    )
    session_id: Annotated[str, Field(alias="sessionId")] = None
    channels: Annotated[list[str], Field(alias="channels")] = None


class SearchScores(BaseModel):
    score_type: Annotated[Literal['search'], Field(alias="scoreType")]
    agg: ScoreAgg = ScoreAgg.SUM
    score_threshold: Annotated[float, Field(alias="scoreThreshold", ge=0.0)] = (
        0.000000001
    )
    weights: str = 'L1C1R1Y1'
    sorting_order: Annotated[SortingOrder, Field(alias="sortingOrder")] = (
        SortingOrder.SCORE
    )
    time_decay: Annotated[CastsTimeDecay, Field(alias="timeDecay")] = (
        CastsTimeDecay.NEVER
    )
    normalize: bool = True


class ReplyScores(BaseModel):
    score_type: Annotated[Literal['reply'], Field(alias="scoreType")]
    agg: ScoreAgg = ScoreAgg.SUM
    score_threshold: Annotated[float, Field(alias="scoreThreshold", ge=0.0)] = (
        0.000000001
    )
    weights: str = 'L1C1R1Y1'
    sorting_order: Annotated[SortingOrder, Field(alias="sortingOrder")] = (
        SortingOrder.RECENT
    )
    time_decay: Annotated[CastsTimeDecay, Field(alias="timeDecay")] = (
        CastsTimeDecay.NEVER
    )
    normalize: bool = True


FeedMetadata = TypeAdapter(
    Annotated[
        Union[TrendingFeed, PopularFeed, FarconFeed, TokenFeed],
        Field(discriminator="feed_type"),
    ]
)

ScoresMetadata = TypeAdapter(
    Annotated[Union[SearchScores, ReplyScores], Field(discriminator="score_type")]
)
