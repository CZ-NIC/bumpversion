from typing import Any
from unittest import TestCase

from bumpversion.serializer import (
    FormatSerializer,
    PEP440Serializer,
    SemVerSerializer,
    StrictFormatter,
)


class StrictFormatterTest(TestCase):
    def test_format(self):
        data: Any = (
            ("", {}, ""),
            ("abc", {}, "abc"),
            ("{a}", {"a": "B"}, "B"),
            ("{a}.{b}", {"a": "B", "b": "A"}, "B.A"),
        )
        for input, kwargs, output in data:
            with self.subTest(input=input, kwargs=kwargs, output=output):
                self.assertEqual(StrictFormatter().format(input, **kwargs), output)

    def test_format_too_many(self):
        message = "Too many arguments for format"
        data: Any = (
            ("", {"a": "A"}),
            ("{a}.{b}", {"a": "B", "b": "A", "c": "C"}),
        )
        for input, kwargs in data:
            with self.subTest(input=input, kwargs=kwargs):
                with self.assertRaisesRegex(TypeError, message):
                    StrictFormatter().format(input, **kwargs)


class FormatSerializerTest(TestCase):
    def setUp(self):
        formats = [
            "{major}.{minor}.{micro}.{nano}",
            "{major}.{minor}.{micro}",
            "{major}",
        ]
        self.serializer = FormatSerializer(formats=formats)

    def test_serialize_ok(self):
        data: Any = (
            ({"major": 1}, "1"),
            ({"major": 1, "minor": 2, "micro": 3}, "1.2.3"),
            ({"major": 1, "minor": 2, "micro": 3, "nano": 4}, "1.2.3.4"),
        )
        for input, output in data:
            with self.subTest(input=input, output=output):
                self.assertEqual(self.serializer(input), output)

    def test_serialize_error(self):
        message = "Version cannot be serialized"
        with self.assertRaisesRegex(ValueError, message):
            self.serializer({"major": 0, "minor": 1})

        with self.assertRaisesRegex(ValueError, message):
            self.serializer({"rc": 0})


class PEP440SerializerTest(TestCase):
    def setUp(self):
        self.serializer = PEP440Serializer()

    def test_serialize_ok(self):
        data: Any = (
            ({"major": 1}, "1"),
            ({"major": 1, "minor": 2}, "1.2"),
            ({"major": 1, "minor": 2, "micro": 3}, "1.2.3"),
            ({"major": 1, "minor": 2, "micro": 3, "rc": 4}, "1.2.3rc4"),
            ({"major": 1, "minor": 2, "micro": 3, "alpha": 4}, "1.2.3a4"),
            ({"major": 1, "minor": 2, "micro": 3, "beta": 4}, "1.2.3b4"),
            ({"major": 1, "minor": 2, "micro": 3, "post": 4}, "1.2.3.post4"),
            (
                {"major": 1, "minor": 2, "micro": 3, "alpha": 4, "post": 5},
                "1.2.3a4.post5",
            ),
            ({"major": 1, "minor": 2, "micro": 3, "dev": 4}, "1.2.3.dev4"),
            (
                {"major": 1, "minor": 2, "micro": 3, "post": 4, "dev": 5},
                "1.2.3.post4.dev5",
            ),
            ({"major": 1, "minor": 2, "micro": 3, "local": "abcdef"}, "1.2.3+abcdef"),
            ({"epoch": 0, "major": 1, "minor": 2, "micro": 3}, "0!1.2.3"),
        )
        for input, output in data:
            with self.subTest(input=input, output=output):
                self.assertEqual(self.serializer(input), output)


class SemVerSerializerTest(TestCase):
    def test_serialize(self):
        serializer = SemVerSerializer()
        data: Any = (
            ({"major": 1, "minor": 2}, "1.2.0"),
            ({"major": 1, "prerelease": "rc.2"}, "1.0.0-rc.2"),
            ({"major": 1, "prerelease": "rc.2", "build": "abcd"}, "1.0.0-rc.2+abcd"),
        )

        for input, output in data:
            with self.subTest(input=input, output=output):
                self.assertEqual(serializer(input), output)
