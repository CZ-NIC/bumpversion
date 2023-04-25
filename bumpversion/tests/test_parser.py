"""Unittests for parser module."""
from unittest import TestCase

from bumpversion.parser import PEP440Parser, RegexParser, SemVerParser


class RegexParserTest(TestCase):
    """Unittest for RegexParser."""

    def test_parsing(self):
        parser = RegexParser(r"(?P<major>\d+)\.(?P<minor>\d+)")
        self.assertEqual(parser("2.3"), {"major": "2", "minor": "3"})

    def test_parse_error(self):
        parser = RegexParser(r"(?P<major>\d+)\.(?P<minor>\d+)")
        with self.assertRaisesRegex(ValueError, "Version 2.a does not match regex"):
            parser("2.a")


class PEP440ParserTest(TestCase):
    """Unittests for PEP440Parser."""

    def test_parsing(self):
        data = (
            ("1.2.0", {"major": "1", "minor": "2", "micro": "0"}),
            (
                "1.0.0rc2",
                {"major": "1", "minor": "0", "micro": "0", "rc": "2"},
            ),
            (
                "1.0.0rc2+abcd",
                {"major": "1", "minor": "0", "micro": "0", "rc": "2", "local": "abcd"},
            ),
            (
                "1.2.3.post4.dev5",
                {"major": "1", "minor": "2", "micro": "3", "post": "4", "dev": "5"},
            ),
            (
                "1.2.3.post4.dev",
                {"major": "1", "minor": "2", "micro": "3", "post": "4", "dev": "0"},
            ),
            ("0!1.2.3", {"epoch": "0", "major": "1", "minor": "2", "micro": "3"}),
            ("1.2.3a4", {"major": "1", "minor": "2", "micro": "3", "alpha": "4"}),
            ("1.2.3b4", {"major": "1", "minor": "2", "micro": "3", "beta": "4"}),
            ("1.2.3-c4", {"major": "1", "minor": "2", "micro": "3", "rc": "4"}),
            ("1-alpha4", {"major": "1", "alpha": "4"}),
        )
        parser = PEP440Parser()
        for input, output in data:
            with self.subTest(input=input, output=output):
                self.assertEqual(parser(input), output)


class SemVerParserTest(TestCase):
    """Unittests for SemVerParser."""

    def test_parsing(self):
        data = (
            ("1.2.0", {"major": 1, "minor": 2, "patch": 0, "prerelease": None, "build": None}),
            (
                "1.0.0-rc.2",
                {"major": 1, "minor": 0, "patch": 0, "prerelease": "rc.2", "build": None},
            ),
            (
                "1.0.0-rc.2+abcd",
                {"major": 1, "minor": 0, "patch": 0, "prerelease": "rc.2", "build": "abcd"},
            ),
        )
        parser = SemVerParser()
        for input, output in data:
            with self.subTest(input=input, output=output):
                self.assertEqual(parser(input), output)
