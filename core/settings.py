import os
from pathlib import Path
from typing import Optional, Tuple

import toml as toml
from pydantic import BaseSettings, AnyUrl
from pydantic.env_settings import SettingsSourceCallable


def load_app_configs_from_file(settings: BaseSettings) -> dict:
    """Looking for config.toml file in source directory"""
    file_path = os.path.join(settings.__config__.BASE_DIR, 'config.toml')  # type: ignore

    settings_ = {}

    if os.path.isfile(file_path):
        with open(file_path) as f:
            file_config = toml.load(f)
            flatten_config = _flatten_file_config(file_config)
            for key, value in flatten_config.items():
                settings_[key] = value

    return settings_


def _flatten_file_config(config: dict, key_prefix='') -> dict:
    result = {}
    for key, value in config.items():
        key = key.upper()

        if isinstance(value, dict):
            result.update(_flatten_file_config(value, key_prefix=f'{key_prefix}{key}_'))

        else:
            result[key_prefix + key] = value

    return result


class Settings(BaseSettings):
    PAGES_COUNT: int = 1
    BASE_ITERATION: int = 30000
    # In seconds
    REQUEST_DELAY: int = 2
    RESOURCE_PATH: str = '../resources'
    BASE_URL: str = 'https://stackoverflow.com/questions/{}'

    def get_path(self, path_name):
        return os.path.join(Path(self.__config__.BASE_DIR), Path(getattr(self, path_name)))

    class Config:
        BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        case_sensitive = True
        env_file = ".env"

        @classmethod
        def customise_sources(
                cls,
                init_settings: SettingsSourceCallable,
                env_settings: SettingsSourceCallable,
                file_secret_settings: SettingsSourceCallable,
        ) -> Tuple[SettingsSourceCallable, ...]:
            return (
                init_settings,
                env_settings,
                file_secret_settings,
                load_app_configs_from_file,
            )


settings = Settings()
