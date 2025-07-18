
from utils import config_loader

def test_load_config(tmp_path):
    config_file = tmp_path / "test.yaml"
    config_file.write_text("project:\n  name: test1")
    config = config_loader.load_config(str(config_file))
    assert config["project"]["name"] == "test1"
