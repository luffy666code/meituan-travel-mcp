# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-23

### Added

- Initial public release of the Meituan Travel MCP Server.
- `meituan_travel_query(city, query)` tool — natural-language travel search with city context, powered by Fliggy FlyAI.
- `flyai_ai_search(query)` tool — direct FlyAI ai-search for hotels, attractions, flights, trains, and mixed itineraries.
- stdio MCP server based on the official `mcp` Python SDK (FastMCP).
- Cross-platform support (Windows / Linux / macOS).
- Debug logging via `MEITUAN_TRAVEL_DEBUG` environment variable.

### Notes

- A valid `FLYAI_API_KEY` from the [Fliggy FlyAI Open Platform](https://flyai.open.fliggy.com/console) is required to use the search tools.
- The server shells out to the official `@fly-ai/flyai-cli` Node.js package; no third-party proxy is involved.
