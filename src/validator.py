"""Validation utilities for CLI configuration parameters."""

from pathlib import Path
import re
from urllib.parse import urlparse

PACKAGE_PATTERN = re.compile(r"^[a-zA-Z0-9._+-]+$")
VERSION_PATTERN = re.compile(r"^[a-zA-Z0-9._~+-]+$")
ALLOWED_SCHEMES = ("http", "https")
ALLOWED_EXTENSIONS = (".png",)


class ConfigValidationError(ValueError):
    """Raised when a user-provided configuration parameter is invalid."""


def validate_package_name(name: str) -> str:
    """Validate the target package name."""
    cleaned = name.strip()
    if not cleaned or not PACKAGE_PATTERN.match(cleaned):
        raise ConfigValidationError(
            f"Invalid package name: '{name}'."
        )
    return cleaned


def validate_version(version: str) -> str:
    """Validate the package version string."""
    cleaned = version.strip()
    if not cleaned or not VERSION_PATTERN.match(cleaned):
        raise ConfigValidationError(
            f"Invalid package version: '{version}'."
        )
    return cleaned


def validate_repository(repo: str, test_mode: bool) -> str:
    """Validate repository URL or local test file path."""
    cleaned = repo.strip()
    if not cleaned:
        raise ConfigValidationError("Repository source cannot be empty.")
    if test_mode:
        path = Path(cleaned)
        if not path.is_file():
            raise ConfigValidationError(
                f"Test repository file not found: '{cleaned}'."
            )
        return cleaned
    parsed = urlparse(cleaned)
    if parsed.scheme not in ALLOWED_SCHEMES or not parsed.netloc:
        raise ConfigValidationError(
            f"Invalid repository URL: '{cleaned}'."
        )
    return cleaned


def validate_output_file(filename: str) -> str:
    """Validate output graph image filename."""
    cleaned = filename.strip()
    if not cleaned:
        raise ConfigValidationError("Output filename cannot be empty.")
    path = Path(cleaned)
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ConfigValidationError(
            f"Output file must end with .png: '{cleaned}'."
        )
    if not path.stem:
        raise ConfigValidationError(
            f"Output filename missing base name: '{cleaned}'."
        )
    return cleaned
