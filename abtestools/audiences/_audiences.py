import hashlib
import math
import uuid
from functools import total_ordering
from typing import Any, Literal, Optional, Union

import pandas as pd
from pydantic.main import BaseModel
from scipy.stats import norm

from abtestools._utils.log import PabLog

lg = PabLog(__name__)


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


@total_ordering
class User(BaseModel):
    identifier: Any
    uuid: uuid.UUID
    group: Literal["test", "control"] = None
    __isset: bool = False

    def reverse_group(self) -> 'User':
        if self.group == 'test':
            self.group = 'control'
        if self.group =='control':
            self.group = 'test'

        return self

    def __str__(self) -> str:
        return str(self.uuid)

    def __key(self) -> Any:
        return (self.uuid, self.group)

    def __hash__(self) -> int:
        return hash(self.__key())

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, User):
            return self.__key() == other.__key()
        else:
            return NotImplemented

    def __gt__(self, other) -> bool:
        return self.group == "test" and other.group == "control"


class Audience:

    def __init__(
        self,
        users: Union[list[Any] | pd.Series],
        group_mapping: Optional[dict[Any, Literal["test", "control"]]] = None,
    ) -> None:
        if isinstance(users, pd.Series):
            self.users = users.to_list()
        if isinstance(users, list):
            self.users = users
        else:
            raise TypeError(f"{type(users)} not supported")

        self.users: list[User] = [
            User(identifier=user, uuid=uuid.uuid4()) for user in self.users
        ]
        if group_mapping:
            try:
                for u in self.users:
                    u.group = group_mapping.get(u.identifier)
            except Exception:
                lg.log.warning("Could not Map the Groups")

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
        self.users = sorted(self.users)
        return self

    def invert_groups(self) -> 'Audience':
        self.users = list(map(lambda x: x.reverse_group), self.users)

    def __len__(self) -> Union[float, int]:
        return len(self.users)

    def __dict__(self) -> dict:
        return {u.uuid: u.group for u in self.users}

    def __str__(self) -> str:
        return str(self.__dict__())

    def __sizeof__(self) -> int:
        return len(self.users)

    def __getitem__(self, item):
        return self.users[item]
