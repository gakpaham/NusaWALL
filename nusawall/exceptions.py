class NusaWallError(Exception):
    """Base exception for NusaWall."""


class ConfigurationError(NusaWallError):
    """Raised when config validation fails."""
