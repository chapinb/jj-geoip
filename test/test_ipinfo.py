from unittest import TestCase
import responses
from geoip.ipinfo import BulkEnrich, Enrich, URL, location_formatter


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


class IpInfoBulkTestCase(TestCase):
    def setUp(self) -> None:
        self.sample_1_ips = ["1.1.1.1", "2.2.2.2"]
        self.sample_1_response = {
            "2.2.2.2": {
                "ip": "2.2.2.2",
                "city": "Cairo",
                "region": "Cairo",
                "country": "EG",
                "loc": "30.0626,31.2497",
                "org": "AS3215 Orange S.A.",
                "timezone": "Africa/Cairo",
            },
            "1.1.1.1": {
                "ip": "1.1.1.1",
                "hostname": "one.one.one.one",
                "anycast": True,
                "city": "Los Angeles",
                "region": "California",
                "country": "US",
                "loc": "34.0522,-118.2437",
                "org": "AS13335 Cloudflare, Inc.",
                "postal": "90076",
                "timezone": "America/Los_Angeles",
            },
        }
        self.sample_1_expected = [
            {
                "ip": "2.2.2.2",
                "city": "Cairo",
                "region": "Cairo",
                "country": "EG",
                "loc": "Cairo, Cairo, EG",
                "lat": "30.0626",
                "lon": "31.2497",
                "org": "Orange S.A.",
                "asn": "AS3215",
                "timezone": "Africa/Cairo",
            },
            {
                "ip": "1.1.1.1",
                "hostname": "one.one.one.one",
                "anycast": True,
                "city": "Los Angeles",
                "region": "California",
                "country": "US",
                "loc": "Los Angeles, California, US",
                "lat": "34.0522",
                "lon": "-118.2437",
                "org": "Cloudflare, Inc.",
                "asn": "AS13335",
                "postal": "90076",
                "timezone": "America/Los_Angeles",
            },
        ]

    def test_bulk_ip_lookup(self):
        with responses.RequestsMock() as rsps:
            rsps.upsert(
                responses.POST,
                f"{URL}/batch",
                json=self.sample_1_response,
                status=200,
            )

            resp = BulkEnrich().lookup(self.sample_1_ips)

            # Assertions on content
            self.assertEqual(2, len(resp))
            self.assertEqual(resp, self.sample_1_expected)

            # Assertions on request
            self.assertEqual(1, len(rsps.calls))
            self.assertEqual(rsps.calls[0].request.url, f"{URL}/batch")
