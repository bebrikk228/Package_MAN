"""Entry point for Stage 1 CLI prototype."""

import sys
from typing import Sequence

from cli import AppConfig, parse_config
from validator import ConfigValidationError

EXIT_SUCCESS = 0
EXIT_ERROR = 1


def format_config(config: AppConfig) -> str:
    """Format configuration parameters as key=value lines."""
    lines = [
        f"package={config.package}",
        f"repository={config.repository}",
        f"test_mode={config.test_mode}",
        f"version={config.version}",
        f"output={config.output}",
    ]
    return "\n".join(lines)


def run(argv: Sequence[str] | None = None) -> int:
    """Execute the CLI application and handle configuration errors."""
    try:
        config = parse_config(argv)
    except ConfigValidationError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return EXIT_ERROR
    print(format_config(config))
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(run())
