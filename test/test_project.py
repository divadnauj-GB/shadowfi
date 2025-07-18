
import os
import shutil
from core import project

def test_create_project(tmp_path):
    name = "test_chip"
    base_dir = tmp_path / "projects"
    config_template = tmp_path / "template.yaml"
    config_template.write_text("project:\n  name: test_chip")

    project.create_project(name, str(base_dir), str(config_template))
    assert (base_dir / name / "config.yaml").exists()
    assert (base_dir / name / "src").exists()
