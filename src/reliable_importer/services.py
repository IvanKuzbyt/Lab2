import logging
from dataclasses import dataclass
from collections.abc import Iterator
from data_processor.models import InventoryRecord
from .config import AppConfig
from .readers import read_rows
from .validators import validate
from .exceptions import RecordValidationError
from .exporters import export_json

@dataclass
class Statistics:
    valid: int = 0
    invalid: int = 0
    low_stock: int = 0

def import_records(config: AppConfig, stats: Statistics) -> Iterator[InventoryRecord]:
    logger = logging.getLogger(__name__)
    for line, row in read_rows(config.input_path):
        try:
            record = validate(row, line)
        except RecordValidationError as error:
            stats.invalid += 1
            logger.warning("Invalid record at line %s: %s", line, error)
            if not config.skip_invalid:
                raise
            continue
        stats.valid += 1
        if record.quantity < config.threshold:
            stats.low_stock += 1
            logger.warning("Low stock for %s: %s", record.code, record.quantity)
        yield record

def run(config: AppConfig) -> Statistics:
    stats = Statistics()
    export_json(import_records(config, stats), config.output_path)
    return stats
