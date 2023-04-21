from unittest import TestCase

import tomli
from testfixtures import TempDirectory

import bumpversion
from bumpversion.main import main

from .utils import CommandMixin


class MainTest(CommandMixin, TestCase):
    command = main

    def setUp(self):
        self.tmp_dir = TempDirectory()

    def tearDown(self):
        self.tmp_dir.cleanup()

    def test_missing_parts(self):
        """Test comand fails if neither parts nor --new-version is provided."""
        self.assertCommandFail(
            [], stderr="Either parts or --new-version must be defined.", repo=self.tmp_dir.path
        )

    def test_conflict_version(self):
        """Test comand fails if both parts and --new-version are provided."""
        self.assertCommandFail(
            ["major", "--new-version", "42"],
            stderr="Only one of parts or --new-version must be defined.",
            repo=self.tmp_dir.path,
        )

    def test_part(self):
        """Test bump with parts specification."""
        self.tmp_dir.as_path(".bumpversion.toml").write_text(
            '[bumpversion]\ncurrent_version = "0.0.0"\n'
        )

        self.assertCommandSuccess(["major"], repo=self.tmp_dir.path)

        new_config = tomli.loads(self.tmp_dir.as_path(".bumpversion.toml").read_text())
        self.assertEqual(new_config["bumpversion"]["current_version"], "1.0.0")

    def test_new_version(self):
        """Test bump with --new-version."""
        self.tmp_dir.as_path(".bumpversion.toml").write_text(
            '[bumpversion]\ncurrent_version = "0.0.0"\n'
        )

        self.assertCommandSuccess(["--new-version", "1.2.3"], repo=self.tmp_dir.path)

        new_config = tomli.loads(self.tmp_dir.as_path(".bumpversion.toml").read_text())
        self.assertEqual(new_config["bumpversion"]["current_version"], "1.2.3")

    def test_version(self):
        """Test --version."""
        self.assertCommandSuccess(
            ["--version"],
            stdout="bumpversion {}\n".format(bumpversion.__version__),
            repo=self.tmp_dir.path,
        )

    def test_config_file(self):
        """Test bump with --config-file."""
        config_file = "another.toml"
        self.tmp_dir.as_path(config_file).write_text('[bumpversion]\ncurrent_version = "0.0.0"\n')

        self.assertCommandSuccess(["major", "--config-file", config_file], repo=self.tmp_dir.path)

        new_config = tomli.loads(self.tmp_dir.as_path(config_file).read_text())
        self.assertEqual(new_config["bumpversion"]["current_version"], "1.0.0")

    def test_dry_run(self):
        """Test bump with --dry-run."""
        self.tmp_dir.as_path(".bumpversion.toml").write_text(
            '[bumpversion]\ncurrent_version = "0.0.0"\n'
        )

        self.assertCommandSuccess(["major", "--dry-run"], repo=self.tmp_dir.path)

        new_config = tomli.loads(self.tmp_dir.as_path(".bumpversion.toml").read_text())
        self.assertEqual(new_config["bumpversion"]["current_version"], "0.0.0")
