"""Typer option declarations for the Act Operator CLI."""

from __future__ import annotations

from pathlib import Path

import typer

PATH_OPTION = typer.Option(
    None,
    "--path",
    "-p",
    help="Directory where the new Act project will be created",
    file_okay=False,
    dir_okay=True,
    writable=True,
    resolve_path=True,
)

ACT_NAME_OPTION = typer.Option(
    None,
    "--act-name",
    "-a",
    help="Display name of the Act project",
)

CAST_NAME_OPTION = typer.Option(
    None,
    "--cast-name",
    "-c",
    help="Display name of the initial Cast Graph",
)

LANG_OPTION = typer.Option(
    None,
    "--lang",
    "-l",
    help="Language for scaffolded docs (en|kr)",
)

CAST_ACT_PATH_OPTION = typer.Option(
    Path.cwd(),
    "--path",
    "-p",
    help="Path to an existing Act project",
    file_okay=False,
    dir_okay=True,
    exists=True,
    resolve_path=True,
)

NEW_CAST_NAME_OPTION = typer.Option(
    None,
    "--cast-name",
    "-c",
    help="Display name of the Cast to add",
)

NEW_CAST_LANG_OPTION = typer.Option(
    "en",
    "--lang",
    "-l",
    help="Language for scaffolded cast docs (en|kr)",
)
