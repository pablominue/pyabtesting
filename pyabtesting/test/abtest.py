from typing import Any, Literal, Union

import pandas as pd
from pydantic import BaseModel
from scipy.stats import ttest_ind

from pyabtesting.audiences import Audience, User


class Test(BaseModel):
    audience: Audience
    metric: Literal["discrete", "continuous"]
    data: dict[Any, Union[int, float]]

    def significance(self) -> None:
        test = list(filter(lambda x: x.group == "test", self.audience.users))
        control = list(filter(lambda x: x.group == "control", self.audience.users))

        test_data = {k: v for k, v in self.data.items() if k in test}
        control_data = {k: v for k, v in self.data.items() if k in control}

        result = ttest_ind(a=test_data.values(), b=control_data.values())
        print(result)
