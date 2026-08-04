"""Import-level checks — no network, no running server."""
import re

from qr_cow_mcp import __version__
from qr_cow_mcp.server import TOOLS, _client


def test_exactly_eight_tools_with_unique_names():
    names = [t.name for t in TOOLS]
    assert len(names) == 8
    assert len(set(names)) == 8


def test_expected_tool_names():
    assert {t.name for t in TOOLS} == {
        "create_qrcode",
        "render_styled_qrcode",
        "list_qrcodes",
        "get_qrcode",
        "update_qrcode_destination",
        "delete_qrcode",
        "get_qrcode_analytics",
        "me",
    }


def test_every_tool_has_object_schema_and_description():
    for t in TOOLS:
        assert t.inputSchema.get("type") == "object", t.name
        assert t.description and len(t.description) > 20, t.name


def test_version_is_semver():
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)


def test_client_sends_versioned_user_agent():
    import asyncio

    async def check():
        c = _client()
        try:
            # The API measures MCP adoption by this exact format — keep it stable.
            assert c.headers["user-agent"] == f"qr-cow-mcp/{__version__}"
            assert c.headers["content-type"] == "application/json"
        finally:
            await c.aclose()

    asyncio.run(check())
