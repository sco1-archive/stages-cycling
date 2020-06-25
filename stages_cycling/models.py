from __future__ import annotations

import datetime as dt
import typing as t
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from stages_cycling.parser import build_dfs, parse_stages_csv


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
    avg_hr: int

    max_speed: float
    max_watts: int
    max_rpm: int
    max_hr: int

    # Calculation currently unsupported
    total_kilocal: t.Optional[int] = None
    total_kilojoule: t.Optional[int] = None

    @classmethod
    def from_df(cls, stage: pd.DataFrame, name: str) -> StageSummary:
        """Generate a StageSummary from the provided stage DataFrame and identifying name."""
        data = {"name": name}  # Instantiate a dict of input arguments
        data["total_seconds"] = stage.index[-1] - stage.index[0]

        stage_stats = stage.describe()
        # Distances aren't reset by the bike when the stage changes so we need a per-stage delta
        data["total_distance"] = stage_stats["Miles"].loc["max"] - stage_stats["Miles"].loc["min"]
        _, data["avg_speed"], data["avg_watts"], data["avg_hr"], data["avg_rpm"] = stage_stats.loc["mean"]  # noqa: E501
        _, data["max_speed"], data["max_watts"], data["max_hr"], data["max_rpm"] = stage_stats.loc["max"]  # noqa: E501

        return cls(**data)

    def __str__(self):
        return (
            f"{self.name}\n"
            f"Elapsed Time:  {dt.timedelta(seconds=self.total_seconds)}\n"
            f"Distance (mi): {self.total_distance: .2f}\n\n"
            f"Average MPH:   {self.avg_speed:.2f}\n"
            f"Average Watts: {self.avg_watts:.0f}\n"
            f"Average RPM:   {self.avg_rpm:.0f}\n"
            f"Average HR:    {self.avg_hr:.0f}\n\n"
            f"Max MPH:   {self.max_speed:.2f}\n"
            f"Max Watts: {self.max_watts:.0f}\n"
            f"Max RPM:   {self.max_rpm:.0f}\n"
            f"Max HR:    {self.max_hr:.0f}"
        )


@dataclass
class CycleWorkout:
    """Represent the full cycling workout."""

    workout_date: dt.date
    class_type: str

    full_ride: pd.DataFrame
    full_ride_summary: StageSummary

    stages: t.List[pd.DataFrame]
    stage_summaries: t.List[StageSummary]

    @classmethod
    def from_csv(cls, filepath: Path) -> CycleWorkout:
        """Parse the raw Stages CSV log output into a `CycleWorkout` instance."""
        # Split CSV filename into the relevant components
        # CSV filename should be of the form YYYY-MM-DD xxm Class Type.csv, if it isn't then oh well
        date_str, _, class_type = filepath.stem.split(maxsplit=2)
        workout_date = dt.date(*(int(substr) for substr in date_str.split("-")))

        # Parse raw stage data into dataframes
        raw_stages, _ = parse_stages_csv(filepath)
        stages, full_ride = build_dfs(raw_stages)

        # Put full ride as the "0th" stage
        stage_summaries = [StageSummary.from_df(full_ride, name="Full Ride")]
        for idx, stage in enumerate(stages, start=1):
            stage_summaries.append(StageSummary.from_df(stage, name=f"Stage {idx}"))

        return cls(
            workout_date, class_type, full_ride, stage_summaries[0], stages, stage_summaries[1:]
        )

    def __str__(self):
        return (
            f"{self.workout_date} {self.class_type}\n"
            f"Elapsed Time:  {dt.timedelta(seconds=self.full_ride_summary.total_seconds)}\n"
            f"Distance (mi): {self.full_ride_summary.total_distance: .2f}\n\n"
            f"Average MPH:   {self.full_ride_summary.avg_speed:.2f}\n"
            f"Average Watts: {self.full_ride_summary.avg_watts:.0f}\n"
            f"Average RPM:   {self.full_ride_summary.avg_rpm:.0f}\n"
            f"Average HR:    {self.full_ride_summary.avg_hr:.0f}\n\n"
            f"Max MPH:   {self.full_ride_summary.max_speed:.2f}\n"
            f"Max Watts: {self.full_ride_summary.max_watts:.0f}\n"
            f"Max RPM:   {self.full_ride_summary.max_rpm:.0f}\n"
            f"Max HR:    {self.full_ride_summary.max_hr:.0f}"
        )
