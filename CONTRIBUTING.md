# Contributing

Thanks for helping improve the qr-cow MCP server!

## Dev setup

```sh
git clone https://github.com/qrcow/qr_cow_mcp.git
cd qr_cow_mcp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest
```

## Guidelines

- Keep the server a **thin pass-through**: no business logic, no state —
  it forwards tool calls to the qr-cow API and returns the response.
- One PR per change; include a test where practical (`tests/`).
- Tool descriptions are user-facing prompt text for LLMs — write them
  the way you'd want a model to read them (what it does, when to use it,
  limits), not like internal docs.
- Never log or echo the API token. It exists only in the `Authorization`
  header.
- Dependency changes need a reason in the PR description. The `mcp<2`
  cap is deliberate — see the comment in `pyproject.toml`.

## Reporting issues

Open a [GitHub issue](https://github.com/qrcow/qr_cow_mcp/issues) with
the client you used (Claude Desktop / Cursor / …), the tool call that
failed, and the error text. **Redact your `qrc_live_…` token.**

For anything security-sensitive, email hi@qr-cow.com instead of opening
a public issue.
