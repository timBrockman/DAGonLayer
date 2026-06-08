# Publishing `DAGonLayer` to PyPI

## Prerequisites

- Python 3.11+
- `pip install build twine`
- A valid PyPI account and API token

## Build

```bash
python -m build
```

## Publish

```bash
python -m twine upload dist/*
```

## Notes

- If you want to publish to Test PyPI first:

```bash
python -m twine upload --repository testpypi dist/*
```

- Use `~/.pypirc` to store credentials securely.
