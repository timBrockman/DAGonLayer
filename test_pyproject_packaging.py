from pathlib import Path
import tomllib


def test_project_dependencies_are_string_array() -> None:
    pyproject = Path(__file__).resolve().parent / "pyproject.toml"
    data = tomllib.loads(pyproject.read_text(encoding="utf-8"))

    dependencies = data["project"]["dependencies"]

    assert isinstance(dependencies, list)
    assert all(isinstance(dep, str) for dep in dependencies)
