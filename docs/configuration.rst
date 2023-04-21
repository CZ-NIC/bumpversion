Configuration
=============

Configuration files
-------------------

Bumpversion reads its configuration from following files, in this order:

- ``.bumpversion.toml``
- ``pyproject.toml``

The files are searched for in working directory. Only the first file found is used.
Configuration is stored in ``[bumpversion]`` table in ``.bumpversion.toml``
and in ``[tools.bumpversion]`` table in ``pyproject.toml``

Versioning schemas
------------------

If you have a simple use-case, you can use one of the prepared versioning schemas.
Bumpversion currently supports these schemas:

- ``semver`` following `SemVer spec <https://semver.org/>`_
- ``pep440`` following `PEP440 <https://peps.python.org/pep-0440/>`_
  with at most three final release components (``major``, ``minor``, ``micro``)

Both of these schemas provide the same result if you use ``X.Y.Z`` versioning without
any prereleases or other components.
However, ``pep440`` also allows for ``X.Y`` or even just ``X`` while SemVer always requires
exactly three final release components as required by its specification.

When you choose the schema, you can specify it in configuration file:

.. code-block:: toml

   [bumpversion]
   current_version = "0.1.0"
   schema = "pep440"

   [[bumpversion.file]]
   path = "setup.cfg"

   [[bumpversion.file]]
   path = "project/__init__.py"

You can specify custom search and replace patterns for each file:

.. code-block:: toml

   [bumpversion]
   current_version = "0.1.0"
   schema = "pep440"

   [[bumpversion.file]]
   path = "setup.cfg"
   search = "version = {current_version}"
   replace = "version = {new_version}"

   [[bumpversion.file]]
   path = "project/__init__.py"
   search = '__version__ = "{current_version}"'
   replace = '__version__ = "{new_version}"'

Advanced usage example
----------------------

Let's say that you have a project with both Python and JavaScript code.
Since Python packages use PEP440, but npm packages use SemVer, you need to restrict yourself
to common subset of those two schemas. Let's say we want to use ``X.Y.Z`` scheme with optional
``rc`` (release candidate) component.
Bumpversion allows you to specify different serialization for each file if necessary:

.. code-block:: toml

   [bumpversion]
   current_version = "1.0.0"
   schema = "pep440"

   [[bumpversion.file]]
   path = "setup.cfg"
   search = "version = {current_version}"
   replace = "version = {new_version}"

   [[bumpversion.file]]
   path = "package.json"
   search = '\n  "version": "{current_version}",\n'
   replace = '\n  "version": "{new_version}",\n'

   [bumpversion.file.serializer]
   cls = "bumpversion.FormatSerializer"
   formats = [
      "{major}.{minor}.{micro}-rc.{rc}",
      "{major}.{minor}.{micro}",
   ]

When we call ``bumpversion micro rc`` with this configuration, version in ``.bumpversion.toml``
and ``setup.cfg`` is bumped to ``1.1.0rc1``. However, version in ``package.json`` is bumped to
``1.1.0-rc.1`` which is compatible with SemVer specification.
