import os


# Set the PYTTING_SETTINGS_MODULE environment variable globally
def pytest_configure():
    os.environ["PYTTING_SETTINGS_MODULE"] = "tests.settings"
