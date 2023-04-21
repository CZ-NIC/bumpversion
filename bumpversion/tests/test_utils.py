from unittest import TestCase
from unittest.mock import sentinel

from bumpversion.settings import CONFIG_FILES
from bumpversion.utils import import_path, load_instance


class ImportPathTest(TestCase):
    def test_class(self):
        cls = import_path("bumpversion.tests.test_utils.ImportPathTest")
        self.assertEqual(cls, ImportPathTest)

    def test_attribute(self):
        attribute = import_path("bumpversion.settings.CONFIG_FILES")
        self.assertEqual(attribute, CONFIG_FILES)

    def test_invalid(self):
        data = (
            # path, error_message
            ("", "is not a valid dotted path"),
            (".", "Empty module name"),
            (".invalid", "Empty module name"),
            ("invalid", "is not a valid dotted path"),
            ("invalid.", "No module named"),
            ("invalid.path", "No module named"),
            ("invalid..path", "No module named"),
            ("bumpversion.tests.invalid.TestCase", "No module named"),
            ("bumpversion.tests.test_utils.", "does not have a class or attribute"),
            ("bumpversion.tests.test_utils.InvalidTestCase", "does not have a class or attribute"),
        )
        for path, error in data:
            with self.subTest(path=path):
                with self.assertRaisesRegex(ImportError, error):
                    import_path(path)


class TestClass:
    """Test class for load_instance."""

    def __init__(self, *, keyword=None, another=None):
        self.keyword = keyword
        self.another = another


class LoadInstanceTest(TestCase):
    def test_class_only(self):
        obj = load_instance("bumpversion.tests.test_utils.TestClass")

        self.assertIsInstance(obj, TestClass)
        self.assertIsNone(obj.keyword)
        self.assertIsNone(obj.another)

    def test_class_kwargs(self):
        obj = load_instance(
            "bumpversion.tests.test_utils.TestClass",
            keyword=sentinel.value,
            another=sentinel.another,
        )

        self.assertIsInstance(obj, TestClass)
        self.assertEqual(obj.keyword, sentinel.value)
        self.assertEqual(obj.another, sentinel.another)

    def test_invalid_path(self):
        data = (
            # path, error_message
            ("", "is not a valid dotted path"),
            ("bumpversion.tests.test_utils.InvalidTestCase", "does not have a class or attribute"),
        )
        for path, error in data:
            with self.subTest(path=path):
                with self.assertRaisesRegex(ImportError, error):
                    load_instance(path)

    def test_invalid_kwargs(self):
        data = (
            {"invalid": sentinel.invalid},
            {
                "keyword": sentinel.keyword,
                "another": sentinel.another,
                "invalid": sentinel.invalid,
            },
        )
        for kwargs in data:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(TypeError):
                    load_instance("bumpversion.tests.test_utils.TestClass", **kwargs)
