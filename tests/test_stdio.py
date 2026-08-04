"""End-to-end stdio smoke: spawn the installed console script and complete
an MCP initialize + tools/list handshake — exactly what Claude Desktop does."""
import json
import os
import shutil
import subprocess

import pytest

BIN = shutil.which("qr-cow-mcp")


@pytest.mark.skipif(BIN is None, reason="qr-cow-mcp entry point not installed")
def test_stdio_handshake_lists_all_tools():
    proc = subprocess.Popen(
        [BIN],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "QRCOW_API_TOKEN": "qrc_test_smoke"},
    )

    def send(msg):
        proc.stdin.write((json.dumps(msg) + "\n").encode())
        proc.stdin.flush()

    def recv():
        line = proc.stdout.readline()
        assert line, f"server died: {proc.stderr.read().decode()[:500]}"
        return json.loads(line)

    try:
        send({
            "jsonrpc": "2.0", "id": 1, "method": "initialize",
            "params": {
                "protocolVersion": "2025-06-18",
                "capabilities": {},
                "clientInfo": {"name": "smoke", "version": "0"},
            },
        })
        init = recv()
        assert init["result"]["serverInfo"]["name"] == "qr-cow"

        send({"jsonrpc": "2.0", "method": "notifications/initialized"})
        send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = recv()
        names = {t["name"] for t in tools["result"]["tools"]}
        assert len(names) == 8
        assert "render_styled_qrcode" in names
    finally:
        proc.terminate()
        proc.wait(timeout=5)
