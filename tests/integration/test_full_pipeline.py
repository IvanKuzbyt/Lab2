import json
from dataclasses import replace
from pathlib import Path
import pytest
from reliable_importer.config import load_config
from reliable_importer.exceptions import RecordValidationError
from reliable_importer.services import run
from warehouse_manager.main import build_service_from_records
from reliable_importer.readers import read_rows
from reliable_importer.validators import validate

@pytest.mark.integration
def test_csv_to_json_tolerant(tmp_path):
    cfg = replace(load_config(Path("config.yaml")), input_path=Path("data/demo_inventory.csv"), output_path=tmp_path / "out.json", skip_invalid=True)
    stats = run(cfg)
    result = json.loads(cfg.output_path.read_text(encoding="utf8"))
    assert stats.valid == 4 and stats.invalid == 1 and len(result) == 4

@pytest.mark.integration
def test_strict_rollback(tmp_path):
    path = tmp_path / "out.json"
    path.write_text("original")
    cfg = replace(load_config(Path("config.yaml")), input_path=Path("data/demo_inventory.csv"), output_path=path, skip_invalid=False)
    with pytest.raises(RecordValidationError): run(cfg)
    assert path.read_text() == "original"
    assert not list(tmp_path.glob("*.tmp"))

@pytest.mark.integration
def test_import_to_warehouse(tmp_path, csv_file):
    records = [validate(row, line) for line, row in read_rows(csv_file)]
    service = build_service_from_records(records)
    assert service.search("SKU-1") is not None
    assert service.search("SKU-2").quantity == 0
    assert len(service.low_stock()) >= 1
