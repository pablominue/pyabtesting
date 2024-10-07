import hashlib
import math
import uuid
from typing import Any, Literal, Optional, Union

import pandas as pd
from pydantic.main import BaseModel
from scipy.stats import norm


def asign_group_from_uuid(uuid: uuid.UUID, control_threshold) -> str:
    hash_obj = hashlib.sha256(uuid.bytes)
    hash_int = int.from_bytes(hash_obj.digest(), byteorder="big")
    decimal_value = hash_int / (2**256 - 1)

    if decimal_value <= control_threshold:
        return "control"
    else:
        return "test"


def calculate_sample_size(
    baseline_conversion_rate=0,  ## If not provided, maybe calculate the average from a dataframe?
    min_detectable_effect=0.02,  ## Smallest difference between test and holdout groups (2% -> 0.02)
    confidence_level=0.95,
    power=0.80,
    total_users: float = 0,
    control_group_ratio: float = 0.1,
):
    z_alpha = norm.ppf(1 - (1 - confidence_level) / 2)
    z_beta = norm.ppf(power)

    p = baseline_conversion_rate
    delta = min_detectable_effect

    required_sample_size_per_group = (
        2 * (z_alpha + z_beta) ** 2 * p * (1 - p)
    ) / delta**2
    required_sample_size_per_group = math.ceil(
        required_sample_size_per_group
    )  # Round up to nearest integer

    control_group_size = math.ceil(
        total_users * control_group_ratio
    )  # Number of users in control group
    test_group_size = total_users - control_group_size
    if (
        required_sample_size_per_group > control_group_size
        or required_sample_size_per_group > test_group_size
    ):
        raise ValueError(
            f"Not enough users in one of the groups. Required: {required_sample_size_per_group}, Available: Control = {control_group_size}, Test = {test_group_size}"
        )

    return control_group_size, test_group_size, required_sample_size_per_group


class User(BaseModel):
    identifier: Any
    uuid: uuid.UUID
    group: Literal["test", "control"] = None
    __isset: bool = False

    def __str__(self) -> str:
        return str(self.uuid)

    def __eq__(self, other: "User") -> bool:
        return self.uuid == other.uuid


class Audience:

    def __init__(self, users: Union[list[Any] | pd.Series]) -> None:
        if isinstance(users, pd.Series):
            self.users = users.to_list()
        if isinstance(users, list):
            self.users = users
        else:
            raise TypeError

        self.users: list[User] = [
            User(identifier=user, uuid=uuid.uuid4()) for user in self.users
        ]

    def __len__(self) -> Union[float, int]:
        return len(self.users)

    def assign_groups(
        self,
        baseline_conversion_rate=0,
        min_detectable_effect=0.02,
        confidence_level=0.95,
        power=0.80,
        control_group_ratio: float = 0.1,
    ) -> "Audience":
        total_users = self.__len__()

        (control_group_size, test_group_size, required_sample_size_per_group) = (
            calculate_sample_size(
                baseline_conversion_rate=baseline_conversion_rate,
                min_detectable_effect=min_detectable_effect,
                confidence_level=confidence_level,
                power=power,
                control_group_ratio=control_group_ratio,
                total_users=total_users,
            )
        )
        for u in self.users:
            u.group = asign_group_from_uuid(
                u.uuid, control_threshold=control_group_ratio
            )
        print(self.users)
        return self


users = [i + 1 for i in range(10000)]
audience = Audience(users=users)
audience.assign_groups()

for i in audience.users:
    print(i.group)
    break
