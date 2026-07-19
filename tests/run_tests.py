import unittest
from pathlib import Path
import sys

if __name__ == '__main__':
    loader = unittest.TestLoader()
    # Anchor the top-level dir at the project root, so the test modules can
    # import the "tests" package regardless of how the runner is invoked.
    tests_dir = Path(__file__).parent.absolute()
    suite = loader.discover(tests_dir, top_level_dir=tests_dir.parent)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)

    sys.exit(0 if result.wasSuccessful() else 1)
