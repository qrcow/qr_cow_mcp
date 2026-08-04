# qr-cow MCP server

[![PyPI](https://img.shields.io/pypi/v/qr-cow-mcp)](https://pypi.org/project/qr-cow-mcp/)
[![Python](https://img.shields.io/pypi/pyversions/qr-cow-mcp)](https://pypi.org/project/qr-cow-mcp/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CI](https://github.com/qrcow/qr_cow_mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/qrcow/qr_cow_mcp/actions/workflows/ci.yml)

An MCP server that exposes the customer-facing [qr-cow.com](https://qr-cow.com)
API to any MCP-compatible AI client (Claude Desktop, Claude Code, Cursor,
Zed, …).

Once connected, you can say things like:

> "Make a QR code that goes to https://my-cafe.com/menu, call it Café menu"
> "Render a styled QR for https://acme.com in the ocean preset, 600px"
> "Show me which countries scanned my café menu last week"
> "Change the destination of the café menu QR to /menu-v2"

…and the assistant calls the API on your behalf.

---

## 1. Create a token

1. Sign in at https://qr-cow.com.
2. Go to **Dashboard → API & MCP**.
3. Click **Create token**. Give it a name like "Claude Desktop".
4. Copy the `qrc_live_…` value that appears. **It's shown once.**

## 2. Wire it into your MCP client

### Claude Desktop / Claude Code

Add to `~/.claude.json` (or your platform's equivalent config):

```json
{
  "mcpServers": {
    "qr-cow": {
      "command": "uvx",
      "args": ["qr-cow-mcp"],
      "env": {
        "QRCOW_API_TOKEN": "qrc_live_..."
      }
    }
  }
}
```

Restart the client. You should see qr-cow tools listed.

### Cursor / Zed

Same shape — pass `command`, `args`, and an `env` block with
`QRCOW_API_TOKEN`. See their MCP docs for the exact key.

### Self-hosted qr-cow

Set `QRCOW_API_BASE` (defaults to `https://qr-cow.com/api`) to point at
your install:

```json
"env": {
  "QRCOW_API_TOKEN": "qrc_live_...",
  "QRCOW_API_BASE": "https://your-host/api"
}
```

---

## Tools

| Tool | What it does |
|---|---|
| `create_qrcode` | Create and save a static or dynamic QR (URL, Wi-Fi, vCard, …) in your account. |
| `render_styled_qrcode` | Render a fully styled QR image (dot/eye shapes, gradient, logo) from data plus a preset or style, without saving it. Returns the image. |
| `list_qrcodes` | List recent QR codes in your account. |
| `get_qrcode` | Fetch one QR code with its current destination + design. |
| `update_qrcode_destination` | Change a dynamic QR's destination — the printed code keeps working. |
| `delete_qrcode` | Soft-delete a code. |
| `get_qrcode_analytics` | Scans, unique scanners, country / device / hour-of-day breakdown. |
| `me` | The signed-in user's profile + current plan. |

---

## Develop locally

```sh
git clone https://github.com/qrcow/qr_cow_mcp.git
cd qr_cow_mcp
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest

# Try it out — auth doesn't matter for startup
QRCOW_API_TOKEN=qrc_live_local QRCOW_API_BASE=http://localhost:8080/api qr-cow-mcp
```

The server speaks stdio, so the easiest way to manually exercise it is
through an MCP client.

## Privacy & security

- The server is a thin pass-through: your token stays in your MCP client
  config and is only ever sent to the qr-cow API (or the `QRCOW_API_BASE`
  you configure) as a `Bearer` header.
- No telemetry, no third-party calls. Requests carry a
  `User-Agent: qr-cow-mcp/<version>` header so the API can distinguish
  MCP traffic.

## Contributing & releases

- [CONTRIBUTING.md](CONTRIBUTING.md) — dev setup, style, how to send a PR.
- [CHANGELOG.md](CHANGELOG.md) — what changed in each release.
- [RELEASING.md](RELEASING.md) — how maintainers cut a release (tag → CI → PyPI).

## License

[MIT](LICENSE)
