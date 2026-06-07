def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: marca tests como tests de integración"
    )