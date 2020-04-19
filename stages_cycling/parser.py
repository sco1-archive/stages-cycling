import typing as t
from pathlib import Path

N_HEADER_LINES = 3
COL_HEADERS = ("Miles", "MPH", "Watts", "HR", "RPM")


def parse_stages_csv(data_file: Path) -> t.Tuple[t.List[str], t.List[str]]:
    """
    Parse raw Stages cycle output into stage data & summaries.

    Data is returned as a list of the raw strings from the output CSV file.

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
                data_chunk.append(line.strip())  # We want to include this before we reset
                summaries.append(data_chunk)
                data_chunk = []
                continue  # Already appended so we can skip the generic append

            data_chunk.append(line.strip())

        return stages, summaries
