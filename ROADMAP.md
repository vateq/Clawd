# Clawd roadmap

Clawd is an early-stage desktop companion for working with Claude and local MCP integrations.

## Priorities
- [x] Minimal desktop task interface
- [x] Local task history
- [x] Experimental MCP stdio discovery and tool calling
- [ ] Per-tool confirmation and permissions
- [ ] Correct MCP framing, request IDs and compatibility testing
- [ ] Cancel and queue background tasks
- [ ] Desktop notifications and tray integration
- [ ] Usage tracking / limit display
- [ ] Packaging for Windows, macOS and Linux

## Current limitations
The MCP support is experimental. Only use servers you trust: server processes execute locally and there is currently no per-call confirmation or sandbox. The app has not yet been extensively tested across platforms or against a range of MCP servers. API usage is billed/managed through your Anthropic account; this app does not provide a Claude subscription or track subscription limits.
