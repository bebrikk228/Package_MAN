"""Unit tests for Stage 1 CLI configuration and validation."""

from pathlib import Path
import tempfile
import unittest

from cli import parse_config
from main import format_config, run
from validator import ConfigValidationError

EXIT_SUCCESS = 0
EXIT_ERROR = 1


class TestCliConfiguration(unittest.TestCase):
    """Test suite verifying parameter parsing and error handling."""

    def test_valid_url_config(self) -> None:
        """Verify valid parameters with a remote repository URL."""
        argv = [
            "-p",
            "busybox",
            "-r",
            "https://dl-cdn.alpinelinux.org/alpine/v3.20/main",
            "-v",
            "1.36.1-r29",
            "-o",
            "deps.png",
        ]
        config = parse_config(argv)
        self.assertEqual(config.package, "busybox")
        self.assertFalse(config.test_mode)
        output = format_config(config)
        self.assertIn("package=busybox", output)
        self.assertIn("output=deps.png", output)

    def test_valid_test_mode_config(self) -> None:
        """Verify valid parameters when test mode points to a file."""
        with tempfile.NamedTemporaryFile("w", delete=False) as tmp:
            tmp.write("A: B C\n")
            tmp_path = tmp.name
        try:
            argv = [
                "-p",
                "A",
                "-r",
                tmp_path,
                "-t",
                "-v",
                "1.0.0",
                "-o",
                "test_graph.png",
            ]
            code = run(argv)
            self.assertEqual(code, EXIT_SUCCESS)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_invalid_package_name(self) -> None:
        """Verify error when package name contains illegal chars."""
        argv = ["-p", "bad package!", "-r", "https://example.com", "-v", "1.0"]
        with self.assertRaises(ConfigValidationError):
            parse_config(argv)

    def test_invalid_repository_url(self) -> None:
        """Verify error when URL is malformed in standard mode."""
        argv = ["-p", "curl", "-r", "not-a-valid-url", "-v", "8.0.0"]
        with self.assertRaises(ConfigValidationError):
            parse_config(argv)

    def test_missing_test_repository_file(self) -> None:
        """Verify error when test file does not exist in test mode."""
        argv = [
            "-p",
            "A",
            "-r",
            "/nonexistent/repo.txt",
            "-t",
            "-v",
            "1.0",
        ]
        self.assertEqual(run(argv), EXIT_ERROR)

    def test_invalid_version(self) -> None:
        """Verify error when version string is empty or invalid."""
        argv = ["-p", "curl", "-r", "https://example.com", "-v", "   "]
        with self.assertRaises(ConfigValidationError):
            parse_config(argv)

    def test_invalid_output_extension(self) -> None:
        """Verify error when output file does not have .png extension."""
        argv = [
            "-p",
            "curl",
            "-r",
            "https://example.com",
            "-v",
            "8.0.0",
            "-o",
            "graph.jpg",
        ]
        with self.assertRaises(ConfigValidationError):
            parse_config(argv)


if __name__ == "__main__":
    unittest.main()
