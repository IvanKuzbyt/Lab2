import argparse
import logging
from pathlib import Path
from .config import load_config
from .exceptions import ApplicationError
from .services import run

def main() -> int:
    parser = argparse.ArgumentParser(description="Lab 5: reliable warehouse importer")
    parser.add_argument("--config", default="config.yaml")
    args = parser.parse_args()
    try:
        config = load_config(Path(args.config))
        config.log_path.parent.mkdir(parents=True, exist_ok=True)
        logging.basicConfig(filename=config.log_path, level=config.level, encoding="utf-8", format="%(asctime)s | %(levelname)s | %(message)s", force=True)
        stats = run(config)
        print(f"Valid: {stats.valid}; Invalid: {stats.invalid}; Low stock: {stats.low_stock}")
        print(f"JSON output: {config.output_path}")
        return 0
    except (ApplicationError, OSError) as error:
        logging.getLogger(__name__).exception("Processing failed")
        print(f"ERROR: {error}")
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
