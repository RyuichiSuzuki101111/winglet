# winglet/paths.py

import os
from datetime import datetime, timezone
from pathlib import Path

_CUSTOM_KEY = 'WINGLET_PATH'
_DEFAULT_ROOT = Path.home() / '.winglet'

ROOT = Path(os.environ.get(_CUSTOM_KEY, _DEFAULT_ROOT))
CONFIG_FILE = ROOT / 'config.json'
LOG_DIR = ROOT / 'logs'


def log_file() -> Path:
    now = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    return LOG_DIR / f'log-{now}-UTC.txt'


def init_dirs() -> None:
    try:
        ROOT.mkdir(parents=True, exist_ok=True)
    except PermissionError as exc:
        msg = f'Cannot create winglet config directory at {ROOT}.'
        if _CUSTOM_KEY not in os.environ:
            msg += f' You can change the location by setting the "{_CUSTOM_KEY}" environment variable.'
        raise PermissionError(msg) from exc

    try:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
    except PermissionError as exc:
        msg = f'Cannot create winglet log directory at {LOG_DIR}.'
        if _CUSTOM_KEY not in os.environ:
            msg += f' You can change the location by setting the "{_CUSTOM_KEY}" environment variable.'
        raise PermissionError(msg) from exc
