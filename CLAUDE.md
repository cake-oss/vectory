# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Development Commands
- Install in development mode: `uv pip install -e .`
- Lint: `ruff check .`
- Format code: `ruff format .`
- Type check: `pyright`
- Run CLI: `uv run cake_vectory/main.py`

## Code Style Guidelines
- Python 3.12+ required
- Use 4-space indentation
- 100 character line length preferred
- Imports: standard lib first, then third-party, then project-specific
- Use type annotations for all function parameters and return values
- Use snake_case for variables/functions, PascalCase for classes
- Error handling: Use try/except with specific messages via Rich console
- Use Google-style docstrings for all modules and functions
- Format numbers with comma separators in outputs (e.g., `f"{value:,}"`)
- Use Rich library for all CLI output formatting
- Follow existing patterns for CLI commands using Typer
