import csv
from typing import Optional


def create_report(
    filename: str,
    data: list[dict[str, str]],
    columns: Optional[list[str]] = None,
) -> None:
    if not isinstance(columns, list):
        columns = list(data[0].keys())

    with open(filename, "w") as open_file:
        writer = csv.DictWriter(open_file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(data)
