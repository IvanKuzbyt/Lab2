import json
from pathlib import Path
from dataclasses import replace
import pytest
from reliable_importer.config import load_config
from reliable_importer.exceptions import RecordValidationError, ConfigurationError
from reliable_importer.services import run
from reliable_importer.exporters import atomic_output


def test_config():
    assert load_config(Path("config.yaml")).threshold == 10


def test_tolerant(tmp_path):
    config = replace(
        load_config(Path("config.yaml")), input_path=Path("data/demo_inventory.csv"), output_path=tmp_path / "out.json"
    )
    result = run(config)
    assert result.valid == 4 and result.invalid == 1
    assert len(json.loads(config.output_path.read_text())) == 4


def test_strict_preserves_output(tmp_path):
    output = tmp_path / "out.json"
    output.write_text("original")
    config = replace(
        load_config(Path("config.yaml")),
        input_path=Path("data/demo_inventory.csv"),
        output_path=output,
        skip_invalid=False,
    )
    with pytest.raises(RecordValidationError):
        run(config)
    assert output.read_text() == "original"
    assert not list(tmp_path.glob("*.tmp"))


def test_atomic_failure(tmp_path):
    path = tmp_path / "out.json"
    path.write_text("old")
    with pytest.raises(RuntimeError):
        with atomic_output(path) as file:
            file.write("partial")
            raise RuntimeError("simulated")
    assert path.read_text() == "old"
    assert not list(tmp_path.glob("*.tmp"))


def test_bad_config(tmp_path):
    with pytest.raises(ConfigurationError):
        load_config(tmp_path / "missing.yaml")


def test_exception_chaining():
    from reliable_importer.validators import validate

    with pytest.raises(RecordValidationError) as caught:
        validate({"code": "X", "name": "Item", "quantity": "wrong", "price": "2", "category": "C"}, 2)
    assert isinstance(caught.value.__cause__, ValueError)
