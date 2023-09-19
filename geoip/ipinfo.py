from typing import Callable, Optional
import requests

URL = "https://ipinfo.io"


def location_formatter(record: dict[str, str]) -> dict[str, str]:
    """Format the IPInfo.io response for our users."""

    # Break the lat and lon into separate fields
    # We can use this to make a KML file later
    loc = record.get("loc", "")
    record["lat"] = loc.split(",")[0].strip()
    record["lon"] = loc.split(",")[-1].strip()

    # Split the ASN from the Organization name
    if record.get("org", "").startswith("AS"):
        asn = record["org"].split(" ")[0]
        record["asn"] = asn
        record["org"] = record["org"].split(" ", 1)[-1]

    # Generate a single line location
    loc_data = []  # Clear the value
    if city := record["city"]:
        loc_data.append(city)
    if region := record["region"]:
        loc_data.append(region)
    if country := record["country"]:
        loc_data.append(country)
    # Join only the available resolutions together
    record["loc"] = ", ".join(loc_data)

    return record


class Enrich:
    def __init__(
        self, api_key: Optional[str] = None, formatter: Optional[Callable] = None
    ):
        self._api_key = api_key

        if formatter:
            self.formatter = formatter
        else:
            self.formatter = location_formatter

    def ask_ipinfo_io(self, ip_address: str) -> dict[str, str]:
        resp = requests.get(
            f"{URL}/{ip_address}",
            params={"token": self._api_key},
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    def lookup(self, ip_addresses: [str, list[str]]) -> list[dict[str, str]]:
        if isinstance(ip_addresses, str):
            ip_addresses = [ip_addresses]

        results = []
        for ip in ip_addresses:
            result = self.ask_ipinfo_io(ip)
            self.formatter(result)
            results.append(result)

        return results


class BulkEnrich(Enrich):
    def __init__(
        self, api_key: Optional[str] = None, formatter: Optional[Callable] = None
    ):
        super().__init__(api_key, formatter)
        self.batch_size = 1000

    def ask_ipinfo_io(self, ip_address: list[str]) -> dict[str, dict[str, str]]:
        resp = requests.post(
            f"{URL}/batch",
            json=ip_address,
            params={"token": self._api_key},
            headers={"Content-Type": "application/json"},
        )
        resp.raise_for_status()
        return resp.json()

    def lookup(self, ip_addresses: [str, list[str]]) -> list[dict[str, str]]:
        if isinstance(ip_addresses, str):
            ip_addresses = [ip_addresses]

        results = []
        for i in range(0, len(ip_addresses), self.batch_size):
            batch = ip_addresses[i : i + self.batch_size]
            enrichments = self.ask_ipinfo_io(batch)
            for enrichment in enrichments.values():
                self.formatter(enrichment)
                results.append(enrichment)

        return results
