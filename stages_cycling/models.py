from __future__ import annotations

import typing as t
from dataclasses import dataclass
from datetime import timedelta

import pandas as pd


@dataclass
class StageSummary:
    """
    Represent the stage or full ride summary information.

    Unless otherwise stated:
        * Distance measurements are miles
        * Speed measurements are miles per hour
    """

    name: str
    total_seconds: int
    total_distance: float

    avg_speed: float
    avg_watts: int
    avg_rpm: int

    max_speed: float
    max_watts: int
    max_rpm: int

    # Calculation currently unsupported
    total_kilocal: t.Optional[int] = None
    total_kilojoule: t.Optional[int] = None

    # HR not currently measured
    avg_hr: t.Optional[int] = None
    max_hr: t.Optional[int] = None

    @classmethod
    def from_df(cls, stage: pd.DataFrame, name: str) -> StageSummary:
        """Generate a StageSummary from the provided stage DataFrame and identifying name."""
        data = {"name": name}  # Instantiate a dict of input arguments
        data["total_seconds"] = stage.index[-1] - stage.index[0]

        stage_stats = stage.describe()
        # Distances aren't reset by the bike when the stage changes so we need a per-stage delta
        data["total_distance"] = stage_stats["Miles"].loc["max"] - stage_stats["Miles"].loc["min"]
        _, data["avg_speed"], data["avg_watts"], data["avg_rpm"] = stage_stats.loc["mean"]
        _, data["max_speed"], data["max_watts"], data["max_rpm"] = stage_stats.loc["max"]

        return cls(**data)

    def __str__(self):
        return (
            f"{self.name}\n"
            f"Elapsed Time:  {timedelta(seconds=self.total_seconds)}\n"
            f"Distance (mi): {self.total_distance}\n\n"
            f"Average MPH:   {self.avg_speed:.2f}\n"
            f"Average Watts: {self.avg_watts:.0f}\n"
            f"Average RPM:   {self.avg_rpm:.0f}\n\n"
            f"Max MPH:   {self.max_speed:.2f}\n"
            f"Max Watts: {self.max_watts:.0f}\n"
            f"Max RPM:   {self.max_rpm:.0f}"
        )
