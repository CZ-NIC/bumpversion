from unittest import TestCase

from bumpversion.schemas import SCHEMAS, Schema, get_schema


class GetSchemaTest(TestCase):
    def test_get_schema(self):
        for component in ("bumper", "parser", "replacer", "serializer"):
            with self.subTest(component=component):
                self.assertEqual(
                    get_schema(Schema.semver, component), SCHEMAS[Schema.semver][component]
                )

    def test_get_schema_unknown_schema(self):
        with self.assertRaisesRegex(ValueError, "Unknown schema Gazpacho"):
            get_schema("Gazpacho", "bumper")  # type: ignore

    def test_get_schema_unknown_schema_part(self):
        with self.assertRaisesRegex(ValueError, "Unknown schema part"):
            get_schema(Schema.semver, "gazpacho")
