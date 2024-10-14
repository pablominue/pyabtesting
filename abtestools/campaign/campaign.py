import datetime
from typing import Any, Callable, Generator, Iterable, Union

import pandas as pd

from abtestools.audiences import Audience, User
from abtestools.test import Metric, Test, TestResult


class CampaignError(Exception):
    pass


class Campaign:
    def __init__(
        self,
        audience: Audience,
        metrics: Iterable[Metric],
        date_range: list[datetime.datetime],
        **kwargs
    ) -> None:

        self.audience = audience
        self.metrics = metrics
        self.dates = date_range

    def calculate_metrics(
        self,
        metric: Metric,
        extract_data: Callable[..., dict[Any, Any]],
        date: datetime.datetime,
        *args,
        **kwargs
    ) -> TestResult:
        data = extract_data(date, *args, **kwargs)
        if not isinstance(data, dict):
            raise TypeError("Extract Data Callable must return dict type")
        if not len(data) == len(self.audience):
            raise CampaignError(
                "Extract Data Function must return DataFrame or Dictionary with length %s",
                len(self.audience),
            )
        return Test(self.audience, metric=metric.type, data=data).test_results()

    def backfill(
        self,
        metric: Metric,
        extract_data: Callable[..., Union[pd.DataFrame, dict[Any, Any]]],
        *args,
        **kwargs
    ) -> Generator[TestResult, Any, Any]:
        for date in self.dates:
            data = extract_data(date, *args, **kwargs)
            yield Test(self.audience, metric.type, data).test_results()
