"""Prompt and validation helpers for the Act Operator CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from .utils import Language, build_name_variants

EXIT_CODE_ERROR = 1
DEFAULT_LANGUAGE_CHOICE = 1

console = Console()


def resolve_path(path_option: Path | None) -> tuple[Path, bool]:
    """Resolve the target path for project creation.

    Args:
        path_option: Optional path provided via CLI option.

    Returns:
        Tuple of (resolved_path, is_custom_path).
    """
    if path_option is not None:
        return path_option.expanduser().resolve(), True

    value = typer.prompt(
        "📂 Please specify the path to create the new Act(Product/Project/Workspace/etc.)",
        default=".",
        show_default=True,
    )
    is_custom = value != "."
    path = Path(value).expanduser().resolve()
    return path, is_custom


def validate_name(name: str) -> None:
    """Validate a name using build_name_variants.

    Args:
        name: Name to validate.

    Raises:
        typer.Exit: If name is invalid.
    """
    try:
        build_name_variants(name)
    except ValueError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error


def check_cast_conflict(cast_snake: str, act_snake: str, act_title: str) -> bool:
    """Check if cast name conflicts with act name.

    Args:
        cast_snake: Snake case version of Cast name.
        act_snake: Snake case version of Act name.
        act_title: Title case version of Act name.

    Returns:
        True if there's a conflict, False otherwise.
    """
    if cast_snake == act_snake:
        console.print(
            f"[red]❌ Cast name conflicts with Act name '{act_title}'.[/red]\n"
            f"[yellow]Both resolve to the same workspace member: '{cast_snake}'[/yellow]\n"
            "[yellow]Please choose a different name for the Cast.[/yellow]"
        )
        return True
    return False


def resolve_name(prompt_message: str, value: str | None) -> str:
    """Resolve Act or Cast name from option or prompt with validation.

    Args:
        prompt_message: Message to display when prompting user.
        value: Optional name value from CLI option.

    Returns:
        Validated name string.
    """
    if value:
        value = value.strip()
        validate_name(value)
        return value

    while True:
        prompted = typer.prompt(prompt_message).strip()
        if not prompted:
            console.print("[red]A value is required.[/red]")
            continue

        try:
            build_name_variants(prompted)
            return prompted
        except ValueError as error:
            console.print(f"[red]❌ {error}[/red]")
            console.print("[yellow]Please try again with a valid name.[/yellow]")


def resolve_cast_name(
    prompt_message: str,
    value: str | None,
    act_snake: str,
    act_title: str,
) -> str:
    """Resolve Cast name with validation and conflict checking against Act name.

    Args:
        prompt_message: Message to display when prompting user.
        value: Optional name value from CLI option.
        act_snake: Snake case version of Act name.
        act_title: Title case version of Act name.

    Returns:
        Validated Cast name string.
    """
    if value:
        value = value.strip()
        validate_name(value)
        cast_variants = build_name_variants(value)
        if check_cast_conflict(cast_variants.snake, act_snake, act_title):
            raise typer.Exit(code=EXIT_CODE_ERROR)
        return value

    while True:
        prompted = typer.prompt(prompt_message).strip()
        if not prompted:
            console.print("[red]A value is required.[/red]")
            continue

        try:
            cast_variants = build_name_variants(prompted)
            if check_cast_conflict(cast_variants.snake, act_snake, act_title):
                continue
            return prompted
        except ValueError as error:
            console.print(f"[red]❌ {error}[/red]")
            console.print("[yellow]Please try again with a valid name.[/yellow]")


def normalize_lang(value: str | None) -> str:
    """Normalize language value to language code string.

    Args:
        value: Language code or None.

    Returns:
        Language code string ("en" or "kr").
    """
    try:
        lang = Language.from_string(value)
        return lang.value
    except ValueError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=EXIT_CODE_ERROR) from error


def select_language_menu() -> str:
    """Display interactive language selection menu.

    Returns:
        Language code string ("en" or "kr").
    """
    console.print(
        "🌐 Choose template language - This option sets the language for "
        "the entire scaffolded template content.\n"
        f"1. {Language.ENGLISH.display_name} ({Language.ENGLISH.value.upper()})\n"
        f"2. {Language.KOREAN.display_name} ({Language.KOREAN.value.upper()})"
    )
    options = {1: Language.ENGLISH, 2: Language.KOREAN}
    while True:
        choice: int = typer.prompt(
            "Enter the number of your language choice (default is 1)",
            default=DEFAULT_LANGUAGE_CHOICE,
            type=int,
        )
        if choice in options:
            return options[choice].value
        console.print("[red]❌ Invalid choice. Please try again.[/red]")


def resolve_language(language: str | None) -> str:
    """Resolve language to language code.

    Args:
        language: Language code string or None.

    Returns:
        Language code string ("en" or "kr").
    """
    if language and language.strip():
        try:
            lang = Language.from_string(language)
            return lang.value
        except ValueError as error:
            console.print(f"[red]{error}[/red]")
            raise typer.Exit(code=EXIT_CODE_ERROR) from error

    return select_language_menu()
