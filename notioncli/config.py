from dataclasses import asdict, dataclass, replace
import os
import os.path
from pathlib import Path
from typing import Optional

import toml

DEFAULT_CONFIG_FILE = os.path.expanduser("~/.local/config/notion/cli.toml")


class ConfigError(ValueError):
    pass


@dataclass
class Config:
    config_file: Path
    token: Optional[str]
    page: Optional[str]

    def is_stored_in_file(self, key):
        return key != "config_file"

    @classmethod
    def from_file(cls):
        config_file = Path(os.environ.get("NOTION_CONFIG", DEFAULT_CONFIG_FILE))
        try:
            with open(config_file, "r") as f:
                config = toml.load(f)
        except FileNotFoundError:
            config = dict()

        return cls(
            config_file=config_file,
            token=config.get("token", None),
            page=config.get("page", None),
        )

    def set(self, **kwargs):
        # TODO: Warn about this?
        if "config_file" in kwargs:
            kwargs.pop("config_file")
        config = replace(self, **kwargs)

        os.makedirs(self.config_file.parent, exist_ok=True)

        with open(self.config_file, "w") as f:
            toml.dump(asdict(config), f)

        return config

    def validate(self):
        if not self.token:
            raise ConfigError("Missing notion token")
        if not self.page:
            raise ConfigError("Missing notion page")
