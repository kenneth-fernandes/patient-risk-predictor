"""Test runner script for the Patient Risk Predictor application."""

import subprocess
import sys


def run_tests(test_type="all", verbose=True, coverage=True):
    """
    Run tests with different configurations.

    Args:
        test_type (str): Type of tests to run ("unit", "integration", "all")
        verbose (bool): Whether to run in verbose mode
        coverage (bool): Whether to include coverage reporting
    """

    # Base pytest command
    cmd = ["python", "-m", "pytest"]

    # Add verbosity
    if verbose:
        cmd.append("-v")

    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=src", "--cov-report=term-missing", "--cov-report=html:htmlcov"])

    # Add test selection based on type
    if test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration":
        cmd.append("tests/integration/")
    elif test_type == "all":
        cmd.append("tests/")
    else:
        print(f"Unknown test type: {test_type}")
        return False

    # Run the tests
    print(f"Running {test_type} tests...")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ {test_type.title()} tests completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ {test_type.title()} tests failed with exit code {e.returncode}")
        return False


def run_specific_test(test_path, verbose=True):
    """
    Run a specific test file or test function.

    Args:
        test_path (str): Path to specific test (e.g., "tests/unit/api/test_app.py::TestHealthCheck")
        verbose (bool): Whether to run in verbose mode
    """
    cmd = ["python", "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    cmd.append(test_path)

    print(f"Running specific test: {test_path}")
    print(f"Command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print("\n✅ Test completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Test failed with exit code {e.returncode}")
        return False


def main():
    """Main test runner function."""
    if len(sys.argv) == 1:
        # No arguments, run all tests
        success = run_tests("all")
    elif sys.argv[1] in ["unit", "integration", "all"]:
        # Run specific test type
        success = run_tests(sys.argv[1])
    elif sys.argv[1] == "quick":
        # Quick run without coverage
        success = run_tests("unit", coverage=False)
    elif sys.argv[1].startswith("tests/"):
        # Run specific test file
        success = run_specific_test(sys.argv[1])
    else:
        print("Usage:")
        print("  python tests/test_runner.py [unit|integration|all|quick]")
        print("  python tests/test_runner.py tests/path/to/specific/test.py")
        print("\nExamples:")
        print("  python tests/test_runner.py unit")
        print("  python tests/test_runner.py integration")
        print("  python tests/test_runner.py all")
        print("  python tests/test_runner.py quick")
        print("  python tests/test_runner.py tests/unit/api/test_app.py")
        success = False

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
