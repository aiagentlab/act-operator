from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from act_operator.cli import app

runner = CliRunner()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_init_creates_scaffold(tmp_path: Path) -> None:
    target_dir = tmp_path / "sample-act"

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
            "en",
        ],
    )
    assert result.exit_code == 0, result.stdout

    project_pyproject = target_dir / "pyproject.toml"
    cast_readme = target_dir / "casts" / "primary_cast" / "README.md"

    assert project_pyproject.exists()
    assert cast_readme.exists()
    assert "Sample Act" in _read(project_pyproject)
    assert "Primary Cast" in _read(cast_readme)


def test_init_derives_act_name_from_path(tmp_path: Path) -> None:
    target_dir = tmp_path / "custom-act"

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

    project_pyproject = target_dir / "pyproject.toml"
    assert "custom-act" in _read(project_pyproject)


def _create_sample_project(tmp_path: Path, lang: str = "en") -> Path:
    """Helper to scaffold a sample Act project for testing."""
    target_dir = tmp_path / "sample-act"
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
    assert result.exit_code == 0, result.stdout
    return target_dir


def test_upgrade_replaces_skills(tmp_path: Path) -> None:
    target_dir = _create_sample_project(tmp_path)
    skill_file = target_dir / ".claude" / "skills" / "testing-cast" / "SKILL.md"
    assert skill_file.exists()

    # Corrupt a skill file
    original = _read(skill_file)
    skill_file.write_text("corrupted content", encoding="utf-8")
    assert _read(skill_file) == "corrupted content"

    # Upgrade should restore it
    result = runner.invoke(app, ["upgrade", "--path", str(target_dir)])
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.exit_code == 0, combined
    assert "upgraded successfully" in combined
    assert _read(skill_file) == original


def test_upgrade_creates_backup(tmp_path: Path) -> None:
    target_dir = _create_sample_project(tmp_path)
    skills_dir = target_dir / ".claude" / "skills"
    assert skills_dir.exists()

    result = runner.invoke(app, ["upgrade", "--path", str(target_dir)])
    assert result.exit_code == 0, result.stdout

    backup_dir = target_dir / ".claude" / "skills.bak"
    assert backup_dir.exists()
    assert (backup_dir / "testing-cast").exists()


def test_upgrade_fails_on_invalid_project(tmp_path: Path) -> None:
    invalid_dir = tmp_path / "not-a-project"
    invalid_dir.mkdir()

    result = runner.invoke(app, ["upgrade", "--path", str(invalid_dir)])
    assert result.exit_code != 0


def test_init_aborts_on_non_empty_dir(tmp_path: Path) -> None:
    target_dir = tmp_path / "existing"
    target_dir.mkdir()
    (target_dir / "existing.txt").write_text("data", encoding="utf-8")

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

    assert result.exit_code != 0
    combined_output = (result.stdout or "") + (result.stderr or "")
    assert "The specified directory already exists and is not empty" in combined_output
