import datetime
from typing import Any, Callable, Generator, Iterable, Optional, Union

import pandas as pd

from abtestools.audiences import Audience, User
from abtestools.test import Metric, Test, TestResult


class CampaignError(Exception):
    pass


class Campaign:
    """
    ## Description
    Class meant to organise the tests and audiences of a specific Marketing Campaign

    -------------------
    ### Parameters
    - audience: Audience object containing the test and control groups
    - metrics: Iterable of Metric objects containing the target metrics of the campaign
    - date_range: [Optional] Date range for the campaign evaluation

    ### Methods
    - calculate_metrics: Returns a TestResult object with the results of the AB Test
    - backfill: If the metric is date-dependant, the backfill method returns a generator with the results of each date.
    """
    def __init__(
        self,
        audience: Audience,
        metrics: Iterable[Metric],
        date_range: Optional[list[datetime.datetime]] = None,
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
        if not self.dates:
            raise CampaignError("Backfill needs the date_range parameter to be set")
        for date in self.dates:
            data = extract_data(date, *args, **kwargs)
            yield Test(self.audience, metric.type, data).test_results()
