# CRUSH.md

## Build/Lint/Test Commands
- **Build**: `pip install -e .`
- **Lint**: `ruff check mychatui`
- **Format**: `ruff format mychatui`
- **Test (all)**: `.venv/bin/python -m pytest`
- **Test (single file)**: `.venv/bin/python -m pytest tests/test_app.py`
- **Test (single method)**: `.venv/bin/python -m pytest tests/test_app.py::TestClass::test_method`

## Code Style
- **Imports**: Group stdlib/third-party/local; sort with `ruff`
- **Formatting**: 4-space indents, max 88 chars (via Ruff)
- **Types**: Type hints for public functions/methods
- **Naming**: `snake_case` for vars/functions, `CamelCase` for classes
- **Errors**: Raise specific exceptions; avoid bare `except`
- **Logging**: Use `logging` module, not `print`

## Notes
- Cursor/Copilot rules: None found
- Added `.crush/` to `.gitignore`