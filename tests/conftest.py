import os


# Set the PYTTING_SETTINGS_MODULE environment variable globally
def pytest_configure():
    os.environ["PYTTING_SETTINGS_MODULE"] = "tests.settings"
    # Required annotation-only settings need values for eager loading.
    os.environ["PYTTING_ONLY_ANNOTATED_INT"] = "42"
    os.environ["PYTTING_ONLY_ANNOTATED_LIST"] = "[1, 2, 3]"
