try:
    from pydantic import BaseModel
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal environments
    class BaseModel:  # type: ignore[no-redef]
        """Minimal BaseModel fallback used when pydantic is unavailable."""

        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)

        @classmethod
        def model_validate(cls, data):
            return cls(**data)

        def model_dump(self, **kwargs):
            return dict(self.__dict__)


class ConfigSchema(BaseModel):
    """Validated configuration object."""

    name: str = "nusawall"
