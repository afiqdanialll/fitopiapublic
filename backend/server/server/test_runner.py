from django.test.runner import DiscoverRunner

class NoDbTestRunner(DiscoverRunner):
    def setup_databases(self, **kwargs):
        pass  # Skip creating the test database

    def teardown_databases(self, old_config, **kwargs):
        pass  # Skip destroying the test database