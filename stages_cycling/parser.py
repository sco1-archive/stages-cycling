import io
import typing as t
from pathlib import Path

import pandas as pd

N_HEADER_LINES = 3
COL_HEADERS = ("Time", "Miles", "MPH", "Watts", "HR", "RPM")


def parse_stages_csv(data_file: Path) -> t.Tuple[t.List[str], t.List[str]]:
    """
    Parse raw Stages cycle output into stage data & summaries.

    Data is returned as a list of the raw strings from the output CSV file. Newlines are retained so
    `pandas.read_csv` can be used with io.StringIO rather than re-reading the CSV file.

    Parsing needs to be done manually if multiple stages are used during the ride, as the bike
    inserts the stage summaries in between the comma-separated data, so the formatting isn't uniform

    NOTE: If multiple stages are present, the last stage will not recieve its own summary table,
    it will instead need to be backed out of the Ride Summary based on the summary data from the
    other stage(s).
    """
    with data_file.open("r") as f:
        # Skip headers
        for _ in range(N_HEADER_LINES):
            f.readline()

        stages = []
        summaries = []
        data_chunk = []
        for line in f:
            if line.startswith("Stage") or line.startswith("Ride"):
                # Stage transition, add stage timeseries data & reset intermediate list
                stages.append(data_chunk)
                data_chunk = []

            if line.startswith("KJ"):
                # End of summary table, add to summary data & reset intermediate list
                data_chunk.append(line)  # We want to include this before we reset
                summaries.append(data_chunk)
                data_chunk = []
                continue  # Already appended so we can skip the generic append

            data_chunk.append(line)
        else:
            # Catch cases where final ride summary is not output
            # If we're in this scenario, once we get to this point there's still data in data_chunk
            if data_chunk:
                stages.append(data_chunk)

        return stages, summaries


def raw_stage_to_df(raw_stage: t.List[str], drop_hr: bool = False) -> pd.DataFrame:
    """
    Convert raw stage CSV to a Pandas DataFrame.

    The heartrate column may be optionally dropped if no monitor is connected. This is not dropped
    by default.
    """
    df = pd.read_csv(io.StringIO("".join(raw_stage)), names=COL_HEADERS, index_col=0)

    # Normalize timestamps to datetime then subtract to create a timedelta for total seconds elapsed
    start = pd.to_datetime("00:00", format="%M:%S")
    deltas = pd.to_datetime(df.index, format="%M:%S") - start
    df.index = deltas.total_seconds()
    df.rename_axis("Elapsed Seconds", inplace=True)

    if drop_hr:
        df.drop(columns="HR", inplace=True)

    return df


def build_dfs(raw_stages: t.List[t.List[str]],) -> t.Tuple[t.List[pd.DataFrame], pd.DataFrame]:
    """Generate dataframes from parsed data & create a concatenated full ride."""
    stage_frames = [raw_stage_to_df(stage) for stage in raw_stages]
    full_ride = pd.concat(stage_frames)

    return stage_frames, full_ride
