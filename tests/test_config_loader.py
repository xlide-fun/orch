import os
from utils.config_loader import load_config

def test_env_override(monkeypatch, tmp_path):
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text("accounts:\n  x:\n    handle: fromfile\n")
    monkeypatch.setenv("X_HANDLE", "fromenv")
    monkeypatch.chdir(tmp_path)
    # load_config reads relative config.yaml
    import shutil
    # write where load looks — cwd
    cfg = load_config(str(cfg_path))
    # our loader uses path arg
    assert cfg["accounts"]["x"].get("handle") == "fromenv"
