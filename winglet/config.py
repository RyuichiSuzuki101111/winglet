# winglet/config.py
from __future__ import annotations

import json
import logging
from typing import ClassVar, TypedDict, cast

from .paths import CONFIG_FILE, init_dirs

logger = logging.getLogger(__name__)


class RawConfig(TypedDict):
    app_count_max: int
    idle_app_count: int


class Config:
    DEFAULT_APP_COUNT_MAX = 5
    DEFAULT_IDLE_APP_COUNT = 2
    APP_COUNT_MAX_KEY = 'app_count_max'
    IDLE_APP_COUNT_KEY = 'idle_app_count'
    CONFIG_KEYS: ClassVar[frozenset[str]] = frozenset(
        (APP_COUNT_MAX_KEY, IDLE_APP_COUNT_KEY),
    )

    def __init__(self) -> None:
        # will be set in _load().
        self._raw: RawConfig
        init_dirs()
        self._load()

    @property
    def app_count_max(self) -> int:
        return cast(
            int,
            self._raw.get(self.APP_COUNT_MAX_KEY, self.DEFAULT_APP_COUNT_MAX),
        )

    @property
    def idle_app_count(self) -> int:
        return cast(
            int,
            self._raw.get(self.IDLE_APP_COUNT_KEY, self.DEFAULT_IDLE_APP_COUNT),
        )

    def _load(self) -> None:
        content: RawConfig
        if not CONFIG_FILE.exists():
            content = {
                'app_count_max': self.DEFAULT_APP_COUNT_MAX,
                'idle_app_count': self.DEFAULT_IDLE_APP_COUNT,
            }

            with CONFIG_FILE.open('w', encoding='UTF-8') as ofile:
                json.dump(content, ofile)
        else:
            with CONFIG_FILE.open('r', encoding='UTF-8') as ifile:
                content_ = json.load(ifile)

            if not isinstance(content_, dict):
                msg = (
                    'invalid winglet config file format. expected dict with keys: '
                    + ', '.join(self.CONFIG_KEYS)
                )
                raise ValueError(msg)

            config_keys = set(content_.keys())

            missing_keys = self.CONFIG_KEYS - config_keys
            if missing_keys:
                logger.warning(
                    'missing key(s) found in winglet config file: %s. expected keys: %s',
                    ', '.join(sorted(missing_keys)),
                    ', '.join(sorted(self.CONFIG_KEYS)),
                )
                content_.setdefault(self.APP_COUNT_MAX_KEY, self.DEFAULT_APP_COUNT_MAX)
                content_.setdefault(
                    self.IDLE_APP_COUNT_KEY,
                    self.DEFAULT_IDLE_APP_COUNT,
                )

            unexpected_keys = config_keys - self.CONFIG_KEYS
            if unexpected_keys:
                logger.warning(
                    'unexpected key(s) found in winglet config file: %s. expected keys: %s',
                    ', '.join(sorted(unexpected_keys)),
                    ', '.join(sorted(self.CONFIG_KEYS)),
                )

            content = cast(RawConfig, content_)

        self._raw = content
