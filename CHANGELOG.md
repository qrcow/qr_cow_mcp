# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.1] - 2026-08-04

First public release, extracted from the qr-cow monorepo into this
standalone repository.

### Added
- `User-Agent: qr-cow-mcp/<version>` header on every API call.
- MIT license, PyPI packaging metadata, CI, and release automation.

### Fixed
- Pinned `mcp>=1.0.0,<2`: mcp 2.0 removed the decorator-based low-level
  `Server` API this server is written against, so an unpinned fresh
  install crashed on import.

## [0.1.0] - 2026-07-01

Internal release inside the qr-cow monorepo.

### Added
- Initial MCP server with 8 tools: `create_qrcode`,
  `render_styled_qrcode` (returns the rendered image), `list_qrcodes`,
  `get_qrcode`, `update_qrcode_destination`, `delete_qrcode`,
  `get_qrcode_analytics`, `me`.

[Unreleased]: https://github.com/qrcow/qr_cow_mcp/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/qrcow/qr_cow_mcp/releases/tag/v0.1.1
