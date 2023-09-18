from unittest import TestCase
import responses
from geoip.ipinfo import Enrich, URL, location_formatter


class IpInfoTestCase(TestCase):
    def setUp(self) -> None:
        self.sample_1_ip = "216.250.210.88"
        self.sample_1_rsp = {
            "ip": "216.250.210.88",
            "city": "SeaTac",
            "region": "Washington",
            "country": "US",
            "loc": "47.4485,-122.2922",
            "org": "AS22351 INTELSAT GLOBAL SERVICE CORPORATION",
            "postal": "98158",
            "timezone": "America/Los_Angeles",
            "hostname": "example.com",
            "anycast": False,
        }
        self.sample_1_expected = {
            "ip": "216.250.210.88",
            "loc": "SeaTac, Washington, US",
            "city": "SeaTac",
            "region": "Washington",
            "country": "US",
            "lat": "47.4485",
            "lon": "-122.2922",
            "org": "INTELSAT GLOBAL SERVICE CORPORATION",
            "asn": "AS22351",
            "postal": "98158",
            "timezone": "America/Los_Angeles",
            "hostname": "example.com",
            "anycast": False,
        }

    def test_formatter(self):
        self.assertNotEqual(self.sample_1_rsp, self.sample_1_expected)
        location_formatter(self.sample_1_rsp)
        self.assertEqual(self.sample_1_rsp, self.sample_1_expected)

    def test_single_ip_lookup(self):
        with responses.RequestsMock() as rsps:
            rsps.upsert(
                responses.GET,
                f"{URL}/{self.sample_1_ip}",
                json=self.sample_1_rsp,
                status=200,
            )

            resp = Enrich().lookup(self.sample_1_ip)

            # Assertions on content
            self.assertEqual(1, len(resp))
            self.assertEqual(resp, [self.sample_1_expected])

            # Assertions on request
            self.assertEqual(1, len(rsps.calls))
            self.assertEqual(rsps.calls[0].request.url, f"{URL}/{self.sample_1_ip}")
