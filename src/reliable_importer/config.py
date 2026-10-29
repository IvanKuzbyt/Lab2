from dataclasses import dataclass
from pathlib import Path
import yaml
from .exceptions import ConfigurationError


@dataclass(frozen=True)
class AppConfig:
    input_path: Path
    output_path: Path
    log_path: Path
    threshold: int
    skip_invalid: bool
    level: str


def load_config(path: Path) -> AppConfig:
    try:
        with path.open(encoding="utf-8") as file:
            raw = yaml.safe_load(file)
        if not isinstance(raw, dict):
            raise ValueError("Configuration must be a mapping")
        base = path.resolve().parent
        inp = base / raw["input"]["path"]
        out = base / raw["output"]["path"]
        log = base / raw["logging"]["path"]
        processing = raw["processing"]
        threshold = processing["low_stock_threshold"]
        skip = processing["skip_invalid"]
        level = raw["logging"]["level"]
        if type(threshold) is not int or threshold < 0 or type(skip) is not bool:
            raise ValueError("Invalid processing settings")
        if level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("Invalid logging level")
        if not inp.is_file():
            raise ValueError(f"Input file does not exist: {inp}")
        if inp.resolve() == out.resolve():
            raise ValueError("Input and output must differ")
        return AppConfig(inp, out, log, threshold, skip, level)
    except (OSError, yaml.YAMLError, KeyError, TypeError, ValueError) as error:
        raise ConfigurationError(f"Invalid configuration: {error}") from error
