# Contributing to OpenShift MCP Server

Thank you for considering contributing!

## Setup

1. Clone the repository and install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Configure cluster access as described in the README.

## Running Tests

Run all tests using:
```bash
PYTHONPATH=src pytest tests/
```

## Adding Tools or Prompt Handlers

- Add new tools to `src/openshift_mcp_server/tools.py` with clear docstrings and standardized error handling (return a dict with 'error' and 'details' on failure).
- Add prompt handlers to `src/openshift_mcp_server/prompts.py` with docstrings describing input/output.
- Add/expand tests in `tests/test_server.py` for any new tools or prompts.

## Coding Guidelines

- Use type hints and docstrings for all public functions/classes.
- Log errors with relevant context (namespace, resource name, etc.).
- Prefer returning structured error dicts over plain strings.

## Pull Requests

- Ensure all tests pass before submitting a PR.
- Describe your changes clearly and reference any related issues.

Thank you for helping improve the project!
