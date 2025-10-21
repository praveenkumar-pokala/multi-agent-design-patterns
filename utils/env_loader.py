"""
Utility for loading environment variables.

This module wraps the `dotenv` loader and provides a helper function to load
environment variables from a `.env` file.  It can also validate that
required variables are present.  See the `.env.example` file in the root
directory for an example of how to configure your environment.
"""

from __future__ import annotations

import os
from typing import Iterable, Optional, Any
try:
    from dotenv import load_dotenv  # type: ignore
except ImportError:
    # If python-dotenv is not installed, define a no-op loader
    def load_dotenv(*args: Any, **kwargs: Any) -> None:  # type: ignore
        return None

    # Provide a helpful warning when the user attempts to validate missing env
    import warnings
    warnings.warn(
        "python-dotenv is not installed; environment variables will not be loaded from .env",
        ImportWarning,
    )


def load_env(required_vars: Optional[Iterable[str]] = None) -> None:
    """Load variables from a `.env` file and optionally validate them.

    Parameters
    ----------
    required_vars: Iterable[str] | None
        Names of variables that must be present in the environment.  If any
        variable is missing after loading, a RuntimeError will be raised.

    Notes
    -----
    The `.env` file is searched in the current working directory and parent
    directories.  If it cannot be found, only existing environment variables
    will be used.
    """
    # Load variables from .env into os.environ.  Existing values are not
    # overwritten by default.
    load_dotenv(override=False)

    if required_vars:
        missing = [var for var in required_vars if not os.getenv(var)]
        if missing:
            missing_list = ", ".join(missing)
            raise RuntimeError(
                f"Missing required environment variables: {missing_list}. "
                "Create a `.env` file or export them in your shell."
            )