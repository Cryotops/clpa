import os

def test_path(path):
    return os.path.join(
            os.path.split(__file__)[0],
            'data',
            path
            )

