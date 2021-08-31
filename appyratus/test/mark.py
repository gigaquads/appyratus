from pytest import mark

SUPPORTED_MARKERS = [
    'unit',
    'integration',
    'performance',
    'slow',
    'skip',
    'parametrize',
]


def pytest_configure(config):
    for marker in SUPPORTED_MARKERS:
        config.addinivalue_line("markers", marker)


unit = mark.unit
integration = mark.integration
performance = mark.performance
slow = mark.slow
skip = mark.skip
parametrize = mark.parametrize
