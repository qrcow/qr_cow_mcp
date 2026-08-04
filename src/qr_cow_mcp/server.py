"""
qr-cow MCP server.

Exposes the customer-facing pieces of the qr-cow API (create / list /
delete QR codes, fetch scan analytics) as tools an MCP-compatible AI
client can call.

Auth: this server is a thin pass-through. It pulls the customer's
personal access token out of the ``QRCOW_API_TOKEN`` environment
variable (set in the MCP client's config) and forwards every call to
the qr-cow API with ``Authorization: Bearer <token>``.

Run via:
    QRCOW_API_TOKEN=qrc_live_xxx uvx qr-cow-mcp
or wired into ``mcpServers`` in a Claude Desktop / Claude Code config.
"""
import logging
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import ImageContent, TextContent, Tool

from qr_cow_mcp import __version__

API_BASE = os.environ.get("QRCOW_API_BASE", "https://qr-cow.com/api")
API_TOKEN = os.environ.get("QRCOW_API_TOKEN")

log = logging.getLogger("qr-cow-mcp")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

if not API_TOKEN:
    log.warning(
        "QRCOW_API_TOKEN is unset — every tool call will fail with 401. "
        "Create a token at https://qr-cow.com/dashboard/api and set "
        "QRCOW_API_TOKEN in your MCP client config."
    )

server: Server = Server("qr-cow")


def _client() -> httpx.AsyncClient:
    headers = {
        "Content-Type": "application/json",
        # Identifies MCP traffic server-side. This is how adoption is
        # measured (distinct tokens whose first call carried this UA),
        # so keep the format stable: qr-cow-mcp/<version>.
        "User-Agent": f"qr-cow-mcp/{__version__}",
    }
    if API_TOKEN:
        headers["Authorization"] = f"Bearer {API_TOKEN}"
    return httpx.AsyncClient(base_url=API_BASE, headers=headers, timeout=30.0)


def _text(payload: Any) -> list[TextContent]:
    import json

    return [TextContent(type="text", text=json.dumps(payload, indent=2, default=str))]


# -------------------- tool definitions --------------------------------------

TOOLS: list[Tool] = [
    Tool(
        name="create_qrcode",
        description=(
            "Create and SAVE a QR code in the customer's qr-cow account (it "
            "appears on their dashboard and is tracked). Pick a content type "
            "and pass the content as a string. Static codes are unlimited on "
            "every plan; dynamic codes (editable + scan analytics) have a "
            "per-plan limit (the free plan includes a few). To just render a "
            "styled image without saving, use render_styled_qrcode instead."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Display name"},
                "content_type": {
                    "type": "string",
                    "enum": [
                        "url", "text", "wifi", "vcard", "mecard", "email",
                        "sms", "phone", "event", "location", "social",
                        "crypto", "app",
                    ],
                },
                "content": {
                    "type": "string",
                    "description": "The encoded content (e.g. the URL, the WIFI:T:WPA;… string, etc.).",
                },
                "type": {
                    "type": "string",
                    "enum": ["static", "dynamic"],
                    "default": "static",
                },
                "fg_color": {"type": "string", "description": "Foreground hex, e.g. #1F2937"},
                "bg_color": {"type": "string", "description": "Background hex, e.g. #FFFDF9"},
            },
            "required": ["name", "content_type", "content"],
        },
    ),
    Tool(
        name="render_styled_qrcode",
        description=(
            "Render a fully STYLED QR code image (colours, dot + eye shapes, "
            "gradient, logo, error-correction) from data and a style, WITHOUT "
            "saving it to the account. Great for generating codes in bulk. Use a "
            "`preset` for a ready-made look and/or set `style` fields to override. "
            "Returns the QR as an image (png/jpg) or SVG source. Stateless: this "
            "calls POST /v1/qr/render and stores nothing."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "Content to encode (a URL, text, WIFI:T:WPA;S:..;P:..;; string, vCard, etc.).",
                },
                "preset": {
                    "type": "string",
                    "description": (
                        "Ready-made style. One of: restaurant, cafe, tech, event, retail, "
                        "wedding, healthcare, real-estate, business-card, crypto, sunset, "
                        "ocean, forest, aurora, berry, mono."
                    ),
                },
                "style": {
                    "type": "object",
                    "description": "Explicit style, applied over the preset.",
                    "properties": {
                        "body": {
                            "type": "string",
                            "enum": [
                                "square", "dots", "rounded", "extra-rounded",
                                "classy", "classy-rounded", "vertical-bars", "horizontal-bars",
                            ],
                            "description": "Dot/module shape",
                        },
                        "eye": {"type": "string", "enum": ["square", "rounded", "dots"]},
                        "fg": {"type": "string", "description": "Foreground hex, e.g. #1F2937"},
                        "bg": {"type": "string", "description": "Background hex"},
                        "gradient": {
                            "type": "object",
                            "properties": {
                                "from": {"type": "string"},
                                "to": {"type": "string"},
                                "direction": {"type": "string", "enum": ["horizontal", "vertical", "radial"]},
                            },
                        },
                        "logo": {"type": "string", "description": "Logo as a base64 data URL (data:image/png;base64,...)"},
                        "logo_size": {"type": "number", "minimum": 0.1, "maximum": 0.3},
                        "ecc": {"type": "string", "enum": ["L", "M", "Q", "H"], "description": "Error correction (use Q or H with a logo)"},
                        "transparent_bg": {"type": "boolean"},
                    },
                },
                "size": {"type": "integer", "minimum": 64, "maximum": 2000, "default": 512},
                "format": {"type": "string", "enum": ["png", "jpg", "svg"], "default": "png"},
            },
            "required": ["data"],
        },
    ),
    Tool(
        name="list_qrcodes",
        description="List the customer's recent QR codes, newest first.",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20},
            },
        },
    ),
    Tool(
        name="get_qrcode",
        description="Fetch full details for one QR code by id, including current redirect URL for dynamic codes.",
        inputSchema={
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
    ),
    Tool(
        name="update_qrcode_destination",
        description=(
            "Update a dynamic QR code's destination URL. The printed code "
            "doesn't change — only what scanning it leads to."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "content": {"type": "string", "description": "New destination URL or content"},
            },
            "required": ["id", "content"],
        },
    ),
    Tool(
        name="delete_qrcode",
        description="Soft-delete a QR code. Scans afterwards return 404.",
        inputSchema={
            "type": "object",
            "properties": {"id": {"type": "integer"}},
            "required": ["id"],
        },
    ),
    Tool(
        name="get_qrcode_analytics",
        description=(
            "Fetch scan analytics for one QR code: total scans, unique "
            "scanners, breakdown by country, device, and hour of day."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "id": {"type": "integer"},
                "days": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 365,
                    "default": 30,
                    "description": "Lookback window in days",
                },
            },
            "required": ["id"],
        },
    ),
    Tool(
        name="me",
        description="Return the authenticated user's profile + plan info.",
        inputSchema={"type": "object", "properties": {}},
    ),
]


@server.list_tools()
async def list_tools() -> list[Tool]:
    return TOOLS


# -------------------- tool implementations ----------------------------------


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent | ImageContent]:
    async with _client() as c:
        try:
            if name == "render_styled_qrcode":
                payload: dict[str, Any] = {
                    "data": arguments["data"],
                    "size": arguments.get("size", 512),
                    "format": arguments.get("format", "png"),
                }
                if arguments.get("preset"):
                    payload["preset"] = arguments["preset"]
                if arguments.get("style"):
                    payload["style"] = arguments["style"]
                r = await c.post("/v1/qr/render?json=true", json=payload)
                if r.status_code >= 400:
                    return _text({"error": "http_error", "status": r.status_code, "body": r.text[:2000]})
                data_url = r.json().get("data", {}).get("data_url", "")
                header, _, b64 = data_url.partition(",")
                mime = header[5:].split(";")[0] if header.startswith("data:") else "image/png"
                if mime == "image/svg+xml":
                    import base64 as _b64

                    return [TextContent(type="text", text=_b64.b64decode(b64).decode("utf-8", "replace"))]
                return [
                    ImageContent(type="image", data=b64, mimeType=mime),
                    TextContent(
                        type="text",
                        text=f"Styled QR rendered ({mime}, {payload['size']}px). Not saved to the account.",
                    ),
                ]

            if name == "create_qrcode":
                r = await c.post("/v1/qrcodes", json=arguments)
            elif name == "list_qrcodes":
                limit = arguments.get("limit", 20)
                r = await c.get(f"/v1/qrcodes?limit={limit}")
            elif name == "get_qrcode":
                r = await c.get(f"/v1/qrcodes/{arguments['id']}")
            elif name == "update_qrcode_destination":
                r = await c.patch(
                    f"/v1/qrcodes/{arguments['id']}",
                    json={"content": arguments["content"]},
                )
            elif name == "delete_qrcode":
                r = await c.delete(f"/v1/qrcodes/{arguments['id']}")
            elif name == "get_qrcode_analytics":
                days = arguments.get("days", 30)
                r = await c.get(f"/v1/analytics/qrcodes/{arguments['id']}?days={days}")
            elif name == "me":
                r = await c.get("/v1/auth/me")
            else:
                return _text({"error": "unknown_tool", "name": name})

            if r.status_code >= 400:
                return _text(
                    {
                        "error": "http_error",
                        "status": r.status_code,
                        "body": r.text[:2000],
                    }
                )
            try:
                return _text(r.json())
            except ValueError:
                return _text({"status": r.status_code, "text": r.text})

        except httpx.RequestError as e:
            return _text({"error": "network", "detail": str(e)})


def main() -> None:
    import asyncio

    async def runner() -> None:
        async with stdio_server() as (read, write):
            await server.run(read, write, server.create_initialization_options())

    asyncio.run(runner())


if __name__ == "__main__":
    main()
