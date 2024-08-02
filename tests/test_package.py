import sys
import unittest


class TestPackage(unittest.TestCase):
    def test_import_package(self):
        import codeocean  # noqa

    def test_strenum_install(self):
        """
        Check if the StrEnum backport is installed/not installed as appropriate in the test environment.

        - the backport can only be installed for Python versions < 3.11 (https://pypi.org/project/backports.strenum/)
        - for >= 3.11, the stdlib StrEnum should be used instead
        """
        if sys.version_info >= (3, 11):
            with self.assertRaises(ImportError):
                import backports.strenum  # noqa
        else:
            try:
                import backports.strenum  # noqa
            except ImportError:
                self.fail("Failed to import the backports.strenum module")
