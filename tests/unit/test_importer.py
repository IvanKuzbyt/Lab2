import json
from dataclasses import replace
from pathlib import Path
import pytest
from reliable_importer.config import load_config
from reliable_importer.exceptions import ConfigurationError, RecordValidationError, DataImportError
from reliable_importer.readers import read_rows
from reliable_importer.validators import validate
from reliable_importer.exporters import atomic_output, export_json
from reliable_importer.services import Statistics, import_records

@pytest.mark.parametrize("quantity,price", [("-1", "1"), ("1", "-1"), ("x", "1"), ("1", "NaN")])
def test_invalid_row(quantity, price):
    row = dict(code="SKU", name="Item", quantity=quantity, price=price, category="C")
    with pytest.raises(RecordValidationError): validate(row, 2)

def test_valid_row():
    record = validate(dict(code=" SKU ", name="Item", quantity="0", price="0", category="C"), 2)
    assert record.code == "SKU" and record.quantity == 0

def test_missing_field_exception():
    with pytest.raises(RecordValidationError) as exc:
        validate(dict(code="", name="Item", quantity="1", price="1", category="C"), 8)
    assert exc.value.field == "code" and exc.value.line_number == 8

def test_exception_chaining():
    with pytest.raises(RecordValidationError) as exc:
        validate(dict(code="X", name="Item", quantity="bad", price="1", category="C"), 2)
    assert isinstance(exc.value.__cause__, ValueError)

def test_read_csv(csv_file):
    rows = list(read_rows(csv_file))
    assert len(rows) == 2 and rows[0][0] == 2

def test_bad_header(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("wrong,column\n1,2\n", encoding="utf8")
    with pytest.raises(DataImportError): list(read_rows(path))

def test_config_load():
    assert load_config(Path("config.yaml")).threshold == 10

def test_config_invalid_yaml(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("[invalid", encoding="utf8")
    with pytest.raises(ConfigurationError): load_config(path)

def test_config_missing_input(tmp_path):
    path = tmp_path / "bad.yaml"
    path.write_text("input:\n  path: missing.csv\noutput:\n  path: output.json\nlogging:\n  path: log.txt\n  level: INFO\nprocessing:\n  low_stock_threshold: 5\n  skip_invalid: true\n", encoding="utf8")
    with pytest.raises(ConfigurationError): load_config(path)

def test_config_validation(tmp_path, csv_file):
    path = tmp_path / "bad.yaml"
    path.write_text(f"input:\n  path: {csv_file.name}\noutput:\n  path: output.json\nlogging:\n  path: log.txt\n  level: INVALID\nprocessing:\n  low_stock_threshold: 5\n  skip_invalid: true\n", encoding="utf8")
    with pytest.raises(ConfigurationError): load_config(path)

def test_import_stats(csv_file, tmp_path):
    config = replace(load_config(Path("config.yaml")), input_path=csv_file, output_path=tmp_path / "result.json")
    stats = Statistics()
    rows = list(import_records(config, stats))
    assert len(rows) == 2 and (stats.valid, stats.invalid, stats.low_stock) == (2, 0, 2)

def test_atomic_preserves_file_on_failure(tmp_path):
    output = tmp_path / "out.json"
    output.write_text("old")
    with pytest.raises(RuntimeError):
        with atomic_output(output) as stream:
            stream.write("new")
            raise RuntimeError("failed")
    assert output.read_text() == "old"
    assert not list(tmp_path.glob("*.tmp"))

def test_export_json(tmp_path):
    record = validate(dict(code="SKU", name="Item", quantity="1", price="1.5", category="C"), 2)
    target = tmp_path / "sub" / "export.json"
    export_json([record], target)
    assert json.loads(target.read_text(encoding="utf8"))[0]["code"] == "SKU"

def test_environment_monkeypatch(monkeypatch):
    monkeypatch.setenv("WAREHOUSE_TEST_MODE", "isolated")
    import os
    assert os.getenv("WAREHOUSE_TEST_MODE") == "isolated"
