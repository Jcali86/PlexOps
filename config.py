import yaml
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "config.yaml"


def load_config(path=None):
    config_file = Path(path) if path else CONFIG_PATH
    with open(config_file, "r") as f:
        return yaml.safe_load(f)


config = load_config()
