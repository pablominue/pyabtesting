import math

from scipy.stats import norm
from typing import Any, Optional, Literal
import pandas as pd
import uuid
from pydantic.main import BaseModel

def calculate_sample_size(
    baseline_conversion_rate=0,  ## If not provided, maybe calculate the average from a dataframe?
    min_detectable_effect=0.02,  ## Smallest difference between test and holdout groups (2% -> 0.02)
    confidence_level=0.95,
    power=0.80,
    total_users: float = 0,
    control_group_ratio: float = 0.1
):
    z_alpha = norm.ppf(1 - (1 - confidence_level) / 2)
    z_beta = norm.ppf(power)

    p = baseline_conversion_rate
    delta = min_detectable_effect

    required_sample_size_per_group = (2 * (z_alpha + z_beta)**2 * p * (1 - p)) / delta**2
    required_sample_size_per_group = math.ceil(required_sample_size_per_group)  # Round up to nearest integer

    control_group_size = math.ceil(total_users * control_group_ratio)  # Number of users in control group
    test_group_size = total_users - control_group_size   
    if required_sample_size_per_group > control_group_size or required_sample_size_per_group > test_group_size:
        raise ValueError(f"Not enough users in one of the groups. Required: {required_sample_size_per_group}, Available: Control = {control_group_size}, Test = {test_group_size}")
    
    return control_group_size, test_group_size, required_sample_size_per_group 

class User(BaseModel):
    identifier: Any
    uuid: uuid.UUID
    group: Literal['test', 'control'] = None
    isset: bool = False

    @property
    def group(self) -> str:
        return self.group

    @group.setter
    def group(self, group: Literal['test', 'control']) -> None:
        if not isset:
            self.group = group
            isset=True

    def __str__(self) -> str:
        return str(self.uuid)

    def __eq__(self, other: 'User') -> bool:
        return self.uuid == other.uuid

class Audience:

    def __init__(self, users: Optional[list[Any] | pd.Series]) -> None:
        if isinstance(users, pd.Series):
            self.users=users.to_list()
        else:
            raise TypeError

        self.users: list[User] = [User(identifier=user, uuid=uuid.uuid4()) for user in self.users]

