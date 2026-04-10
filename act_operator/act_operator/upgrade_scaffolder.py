"""Upgrade helpers for Act Operator CLI."""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .cast_scaffolder import ensure_act_project
from .project_scaffolder import build_template_context, get_scaffold_root
from .utils import (
    ENCODING_UTF8,
    LANGGRAPH_FILE,
    Language,
    build_name_variants,
    render_cookiecutter_template,
)

EXIT_CODE_ERROR = 1

console = Console()


def detect_project_language(act_path: Path) -> str:
    """Detect project language by checking README.md for Korean characters.

    Args:
        act_path: Path to the Act project.

    Returns:
        Language code string ("en" or "kr").
    """
    readme_path = act_path / "README.md"
    if not readme_path.exists():
        return Language.ENGLISH.value

    try:
        content = readme_path.read_text(encoding=ENCODING_UTF8)
        if any("\uac00" <= char <= "\ud7af" for char in content):
            return Language.KOREAN.value
    except OSError:
        pass

    return Language.ENGLISH.value


def detect_first_cast(act_path: Path):
    """Detect the first Cast from langgraph.json graphs registry.

    Args:
        act_path: Path to the Act project.

    Returns:
        NameVariants for the first registered Cast.
    """
    fallback = build_name_variants("default cast")

    langgraph_path = act_path / LANGGRAPH_FILE
    if not langgraph_path.exists():
        return fallback

    try:
        content = langgraph_path.read_text(encoding=ENCODING_UTF8)
        payload = json.loads(content)
        graphs = payload.get("graphs", {})
        if not graphs:
            return fallback

        first_slug = next(iter(graphs))
        graph_ref = graphs[first_slug]
        parts = graph_ref.split("/")
        for index, part in enumerate(parts):
            if part == "casts" and index + 1 < len(parts):
                cast_snake = parts[index + 1]
                raw_name = cast_snake.replace("_", " ")
                return build_name_variants(raw_name)

        return fallback
    except (OSError, json.JSONDecodeError, ValueError, StopIteration):
        return fallback


def _upgrade_skills(
    scaffold_root: Path, act_path: Path, context: dict[str, str]
) -> int:
    """Render latest skills from scaffold and replace project skills.

    Args:
        scaffold_root: Path to the scaffold template directory.
        act_path: Path to the Act project.
        context: Cookiecutter context variables.

    Returns:
        Number of skill directories upgraded.

    Raises:
        typer.Exit: If rendering or file operations fail.
    """
    with tempfile.TemporaryDirectory(prefix="act_upgrade_") as tmp_dir:
        tmp_path = Path(tmp_dir) / "rendered"
        tmp_path.mkdir()

        try:
            render_cookiecutter_template(scaffold_root, tmp_path, context)
        except Exception as error:
            console.print(f"[red]Failed to render scaffold: {error}[/red]")
            raise typer.Exit(code=EXIT_CODE_ERROR) from error

        rendered_skills = tmp_path / ".claude" / "skills"
        if not rendered_skills.exists():
            console.print("[red]No skills found in scaffold template.[/red]")
            raise typer.Exit(code=EXIT_CODE_ERROR)

        target_claude = act_path / ".claude"
        target_skills = target_claude / "skills"
        backup_skills = target_claude / "skills.bak"

        if backup_skills.exists():
            shutil.rmtree(backup_skills)

        if target_skills.exists():
            shutil.move(str(target_skills), str(backup_skills))
            console.print("[dim]Backed up existing skills to .claude/skills.bak/[/dim]")

        target_claude.mkdir(parents=True, exist_ok=True)
        shutil.copytree(str(rendered_skills), str(target_skills))

        skill_dirs = [entry for entry in rendered_skills.iterdir() if entry.is_dir()]
        return len(skill_dirs)


def upgrade_skills_project(act_path: Path) -> None:
    """Upgrade .claude/skills/ in an existing Act project.

    Args:
        act_path: Path to the existing Act project.
    """
    act_path = act_path.resolve()
    ensure_act_project(act_path)

    language = detect_project_language(act_path)
    act = build_name_variants(act_path.name)
    cast = detect_first_cast(act_path)

    console.print("[bold]Upgrading .claude/skills/ ...[/bold]")

    scaffold_root = get_scaffold_root()
    context = build_template_context(act, cast, language)
    skill_count = _upgrade_skills(scaffold_root, act_path, context)

    lang_display = Language.from_string(language).display_name
    table = Table(show_header=False)
    table.add_row("Act", act.title)
    table.add_row("Language", lang_display)
    table.add_row("Skills", str(skill_count))
    table.add_row("Location", str(act_path / ".claude" / "skills"))
    console.print(table)
    console.print("[bold green]Skills upgraded successfully![/bold green]")
