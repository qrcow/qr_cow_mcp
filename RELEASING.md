# Releasing (maintainers)

Releases are tag-driven: pushing a `v*` tag builds the package and
publishes it to PyPI via GitHub Actions using [trusted
publishing](https://docs.pypi.org/trusted-publishers/) — no API token is
stored anywhere.

## One-time setup (before the first release)

1. Create/sign in to the PyPI account and enable 2FA.
2. Add a **pending publisher** at
   https://pypi.org/manage/account/publishing/ with exactly:
   - PyPI project name: `qr-cow-mcp`
   - Owner: `qrcow`
   - Repository name: `qr_cow_mcp`
   - Workflow name: `release.yml`
   - Environment name: `pypi`
3. In this GitHub repo: Settings → Environments → create an environment
   named `pypi` (no secrets needed; optionally add yourself as a
   required reviewer to gate releases).

## Cutting a release

1. Update the version in **both** places (they must match):
   - `pyproject.toml` → `version = "X.Y.Z"`
   - `src/qr_cow_mcp/__init__.py` → `__version__ = "X.Y.Z"`
2. Move the `[Unreleased]` notes in `CHANGELOG.md` under a new
   `[X.Y.Z] - YYYY-MM-DD` heading and update the compare links.
3. Commit, then tag and push:

   ```sh
   git commit -am "release: vX.Y.Z"
   git tag -a vX.Y.Z -m "qr-cow-mcp X.Y.Z"
   git push origin main vX.Y.Z
   ```

4. Watch the `release` workflow. When it's green, verify:

   ```sh
   uvx qr-cow-mcp@latest --help 2>&1 | head -1   # resolves the new version
   ```

## Manual fallback (if Actions is unavailable)

```sh
python -m venv .relvenv && .relvenv/bin/pip install build twine
.relvenv/bin/python -m build
.relvenv/bin/twine check dist/*
.relvenv/bin/twine upload dist/*   # username: __token__, password: pypi-… token
```

## Versioning policy

Semantic versioning. Tool schema changes that could break existing
prompts (renaming a tool, removing a parameter) are **minor** bumps
while we're pre-1.0, and **major** after 1.0. New tools and fixes are
patch/minor as usual.
