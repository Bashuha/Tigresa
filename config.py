import toml
from pathlib import Path


file_path = Path().resolve().joinpath('settings.toml')
toml_config = toml.load(file_path)
TOKEN = toml_config["BOT"]["token"]
