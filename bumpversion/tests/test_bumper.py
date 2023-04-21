"""Unittests for bumper module."""
from unittest import TestCase

from bumpversion.bumper import RegexBumper, SemVerBumper


class SemVerBumperTest(TestCase):
    """Unittests for SemVerBumper."""

    def test_bump(self):
        bumper = SemVerBumper()
        version = {"major": "1", "minor": "1", "patch": "1"}
        scenarios = {
            "major": {"major": 2, "minor": 0, "patch": 0, "prerelease": None, "build": None},
            "minor": {"major": 1, "minor": 2, "patch": 0, "prerelease": None, "build": None},
            "patch": {"major": 1, "minor": 1, "patch": 2, "prerelease": None, "build": None},
            "minor patch": {"major": 1, "minor": 2, "patch": 1, "prerelease": None, "build": None},
            "patch minor": {"major": 1, "minor": 2, "patch": 0, "prerelease": None, "build": None},
            "patch major": {"major": 2, "minor": 0, "patch": 0, "prerelease": None, "build": None},
            "prerelease": {
                "major": 1,
                "minor": 1,
                "patch": 1,
                "prerelease": "rc.1",
                "build": None,
            },
            "prerelease prerelease": {
                "major": 1,
                "minor": 1,
                "patch": 1,
                "prerelease": "rc.2",
                "build": None,
            },
            "build": {"major": 1, "minor": 1, "patch": 1, "prerelease": None, "build": "build.1"},
            "build build": {
                "major": 1,
                "minor": 1,
                "patch": 1,
                "prerelease": None,
                "build": "build.2",
            },
        }
        for part, result in scenarios.items():
            with self.subTest(part=part, result=result):
                self.assertEqual(bumper(version=version, bumped_parts=part.split(" ")), result)

    def test_bump_build_token(self):
        bumper = SemVerBumper(build_token="bbb")
        version = {"major": "1", "minor": "1", "patch": "1"}
        scenarios = {
            "build": {"major": 1, "minor": 1, "patch": 1, "prerelease": None, "build": "bbb.1"},
            "build build": {
                "major": 1,
                "minor": 1,
                "patch": 1,
                "prerelease": None,
                "build": "bbb.2",
            },
        }
        for part, result in scenarios.items():
            with self.subTest(part=part, result=result):
                self.assertEqual(bumper(version=version, bumped_parts=part.split(" ")), result)

    def test_bump_pre_token(self):
        bumper = SemVerBumper(prerelease_token="ppp")
        version = {"major": "1", "minor": "1", "patch": "1"}
        scenarios = {
            "prerelease": {
                "major": 1,
                "minor": 1,
                "patch": 1,
                "prerelease": "ppp.1",
                "build": None,
            },
            "prerelease prerelease": {
                "major": 1,
                "minor": 1,
                "patch": 1,
                "prerelease": "ppp.2",
                "build": None,
            },
        }
        for part, result in scenarios.items():
            with self.subTest(part=part, result=result):
                self.assertEqual(bumper(version=version, bumped_parts=part.split(" ")), result)


class RegexBumperTest(TestCase):
    """Unittests for RegexBumper."""

    def test_bump(self):
        bumper = RegexBumper()
        version = {"major": "1", "minor": "1", "patch": "1"}
        scenarios = {
            "major": {"major": "2", "minor": "0", "patch": "0"},
            "minor": {"major": "1", "minor": "2", "patch": "0"},
            "patch": {"major": "1", "minor": "1", "patch": "2"},
            "minor patch": {"major": "1", "minor": "2", "patch": "1"},
            "patch minor": {"major": "1", "minor": "2", "patch": "0"},
            "patch major": {"major": "2", "minor": "0", "patch": "0"},
            "prerelease": {
                "major": "1",
                "minor": "1",
                "patch": "1",
                "prerelease": "1",
            },
            "prerelease prerelease": {
                "major": "1",
                "minor": "1",
                "patch": "1",
                "prerelease": "2",
            },
            "build": {"major": "1", "minor": "1", "patch": "1", "build": "1"},
            "build build": {
                "major": "1",
                "minor": "1",
                "patch": "1",
                "build": "2",
            },
        }
        for part, result in scenarios.items():
            with self.subTest(part=part, result=result):
                self.assertEqual(bumper(version=version, bumped_parts=part.split(" ")), result)

    def test_bump_nonnumeric(self):
        bumper = RegexBumper()
        version = {"major": "1", "minor": "1", "patch": "1", "prerelease": "p1"}
        scenarios = {
            "major": {"major": "2", "minor": "0", "patch": "0"},
            "minor": {"major": "1", "minor": "2", "patch": "0"},
            "patch": {"major": "1", "minor": "1", "patch": "2"},
            "minor patch": {"major": "1", "minor": "2", "patch": "1"},
            "patch minor": {"major": "1", "minor": "2", "patch": "0"},
            "patch major": {"major": "2", "minor": "0", "patch": "0"},
            "prerelease": {
                "major": "1",
                "minor": "1",
                "patch": "1",
                "prerelease": "p2",
            },
            "prerelease prerelease": {
                "major": "1",
                "minor": "1",
                "patch": "1",
                "prerelease": "p3",
            },
            "build": {"major": "1", "minor": "1", "patch": "1", "prerelease": "p1", "build": "1"},
            "build build": {
                "major": "1",
                "minor": "1",
                "patch": "1",
                "prerelease": "p1",
                "build": "2",
            },
        }
        for part, result in scenarios.items():
            with self.subTest(part=part, result=result):
                self.assertEqual(bumper(version=version, bumped_parts=part.split(" ")), result)

    def test_bump_wrong_nonnumeric(self):
        bumper = RegexBumper()
        with self.assertRaises(ValueError):
            bumper(version={"major": "b"}, bumped_parts=["major"])

    def test_bump_parts_config(self):
        bumper = RegexBumper(
            parts={"minor": {"final": False}, "patch": {"final": False, "start": 5}}
        )
        version = {"major": "1", "minor": "1", "patch": "1"}
        scenarios = {
            "major": {"major": "2"},
            "minor": {"major": "1", "minor": "2"},
            "patch": {"major": "1", "minor": "1", "patch": "2"},
            "minor patch": {"major": "1", "minor": "2", "patch": "5"},
            "patch minor": {"major": "1", "minor": "2"},
            "patch major": {"major": "2"},
        }
        for part, result in scenarios.items():
            with self.subTest(part=part, result=result):
                self.assertEqual(bumper(version=version, bumped_parts=part.split(" ")), result)
