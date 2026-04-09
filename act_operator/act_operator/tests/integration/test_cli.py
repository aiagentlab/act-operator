from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from typer.testing import CliRunner

from act_operator.cli import app

runner = CliRunner()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(_read(path))


def _create_project(tmp_path: Path, *, lang: str = "en") -> Path:
    """Create a reusable baseline Act project for cast-related integration tests."""
    # Given a temporary workspace for integration testing
    target_dir = tmp_path / "sample-act"

    # When a baseline Act project is scaffolded for reuse
    result = runner.invoke(
        app,
        [
            "--path",
            str(target_dir),
            "--act-name",
            "Sample Act",
            "--cast-name",
            "Primary Cast",
            "--lang",
            lang,
        ],
    )

    # Then the setup command should succeed before the test continues
    assert result.exit_code == 0, result.stdout
    return target_dir


def test_init_creates_scaffold(tmp_path: Path) -> None:
    """Test that the root CLI invocation creates the initial Act scaffold."""
    # Given root CLI arguments for a new Act project
    target_dir = _create_project(tmp_path)

    # When the scaffold is created through the root command
    project_pyproject = target_dir / "pyproject.toml"
    cast_readme = target_dir / "casts" / "primary_cast" / "README.md"

    # Then the project files and initial Cast README should exist
    assert project_pyproject.exists()
    assert cast_readme.exists()
    assert "Sample Act" in _read(project_pyproject)
    assert "Primary Cast" in _read(cast_readme)


def test_new_command_creates_scaffold(tmp_path: Path) -> None:
    """Test that the explicit `new` subcommand matches root command behavior."""
    # Given explicit `new` subcommand arguments for a new Act project
    target_dir = tmp_path / "sample-act"

    # When the `new` command is executed
    result = runner.invoke(
        app,
        [
            "new",
            "--path",
            str(target_dir),
            "--act-name",
            "Sample Act",
            "--cast-name",
            "Primary Cast",
            "--lang",
            "en",
        ],
    )

    # Then it should produce the same core scaffold as the root command
    assert result.exit_code == 0, result.stdout
    assert (target_dir / "pyproject.toml").exists()
    assert (target_dir / "casts" / "primary_cast" / "README.md").exists()


def test_init_derives_act_name_from_path(tmp_path: Path) -> None:
    """Test that the Act name is derived from the target path when omitted."""
    # Given a target path but no explicit Act name
    target_dir = tmp_path / "custom-act"

    # When project creation runs
    result = runner.invoke(
        app,
        [
            "--path",
            str(target_dir),
            "--cast-name",
            "Primary Cast",
            "--lang",
            "en",
        ],
    )
    assert result.exit_code == 0, result.stdout

    # Then the project metadata should derive the Act name from the path
    project_pyproject = target_dir / "pyproject.toml"
    assert "custom-act" in _read(project_pyproject)


def test_init_aborts_on_non_empty_dir(tmp_path: Path) -> None:
    """Test that project creation aborts when the target directory is not empty."""
    # Given a target directory that already contains files
    target_dir = tmp_path / "existing"
    target_dir.mkdir()
    (target_dir / "existing.txt").write_text("data", encoding="utf-8")

    # When project creation is attempted
    result = runner.invoke(
        app,
        [
            "--path",
            str(target_dir),
            "--cast-name",
            "Primary Cast",
            "--lang",
            "en",
        ],
    )

    # Then the command should abort instead of overwriting existing content
    assert result.exit_code != 0
    combined_output = (result.stdout or "") + (result.stderr or "")
    assert "The specified directory already exists and is not empty" in combined_output


def test_new_rejects_invalid_language_option(tmp_path: Path) -> None:
    """Test that an unsupported `--lang` value is rejected immediately."""
    # Given a `new` command call with an unsupported `--lang` value
    target_dir = tmp_path / "sample-act"

    # When argument validation runs
    result = runner.invoke(
        app,
        [
            "new",
            "--path",
            str(target_dir),
            "--act-name",
            "Sample Act",
            "--cast-name",
            "Primary Cast",
            "--lang",
            "jp",
        ],
    )

    # Then the command should fail immediately with a language error
    assert result.exit_code != 0
    combined_output = (result.stdout or "") + (result.stderr or "")
    assert "Unsupported language" in combined_output


def test_cast_command_adds_new_cast_to_existing_project(tmp_path: Path) -> None:
    """Test that `act cast` adds a cast package, test file, and langgraph entry."""
    # Given an existing Act project and a new Cast name
    target_dir = _create_project(tmp_path)

    # When `act cast` is executed
    result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(target_dir),
            "--cast-name",
            "Secondary Cast",
            "--lang",
            "en",
        ],
    )

    assert result.exit_code == 0, result.stdout

    cast_dir = target_dir / "casts" / "secondary_cast"
    cast_test = target_dir / "tests" / "cast_tests" / "secondary_cast_test.py"
    langgraph = _read_json(target_dir / "langgraph.json")
    graphs = langgraph["graphs"]

    # Then the new cast package, copied test, and langgraph entry should exist
    assert cast_dir.exists()
    assert (cast_dir / "graph.py").exists()
    assert (cast_dir / "README.md").exists()
    assert cast_test.exists()
    assert "secondary-cast" in graphs
    assert (
        graphs["secondary-cast"]
        == "./casts/secondary_cast/graph.py:secondary_cast_graph"
    )


def test_cast_command_rejects_non_act_project(tmp_path: Path) -> None:
    """Test that `act cast` rejects paths that are not valid Act projects."""
    # Given a directory that does not contain the required Act project files
    invalid_project_dir = tmp_path / "not-an-act"
    invalid_project_dir.mkdir()

    # When `act cast` is executed against that path
    result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(invalid_project_dir),
            "--cast-name",
            "Secondary Cast",
            "--lang",
            "en",
        ],
    )

    # Then the command should reject it as an invalid Act project
    assert result.exit_code != 0
    combined_output = (result.stdout or "") + (result.stderr or "")
    assert "does not look like a valid Act project" in combined_output


def test_cast_command_aborts_when_cast_directory_exists(tmp_path: Path) -> None:
    """Test that `act cast` aborts when the target cast directory already exists."""
    # Given an Act project where the target cast directory already exists
    target_dir = _create_project(tmp_path)

    # When the same Cast is created a second time
    first_result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(target_dir),
            "--cast-name",
            "Secondary Cast",
            "--lang",
            "en",
        ],
    )
    assert first_result.exit_code == 0, first_result.stdout

    second_result = runner.invoke(
        app,
        [
            "cast",
            "--path",
            str(target_dir),
            "--cast-name",
            "Secondary Cast",
            "--lang",
            "en",
        ],
    )

    # Then the command should abort instead of overwriting that Cast
    assert second_result.exit_code != 0
    combined_output = (second_result.stdout or "") + (second_result.stderr or "")
    assert "cast directory already exists and is not empty" in combined_output
