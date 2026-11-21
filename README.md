# Clawd 🧡

A desktop Claude companion for background tasks and Model Context Protocol (MCP) stdio servers. Local UI, task history, and a friendly speech bubble.

**MVP features:** desktop task UI, Anthropic API tool loop, configurable MCP stdio servers, task history, CI syntax check.

## Install
Python 3.10+ and an Anthropic API key are required.

```bash
python -m pip install -r requirements.txt
```

Windows PowerShell:
```powershell
$env:ANTHROPIC_API_KEY="your-key"
python clawd.py
```
macOS/Linux:
```bash
export ANTHROPIC_API_KEY="your-key"
python clawd.py
```
Optional: set `ANTHROPIC_MODEL`. Default model: `claude-sonnet-4-5`.

## MCP
Config is read from `~/.clawd/mcp_servers.json`. Copy `mcp_servers.example.json` there and configure a server you trust:
```json
{
  "servers": [{"name":"sample","command":"npx","args":["-y","YOUR-TRUSTED-MCP-SERVER"],"env":{},"enabled":true}]
}
```
Clawd launches configured MCP subprocesses locally for each task, discovers tools and exposes them to Claude. This implementation is experimental and server compatibility varies.

**Security warning:** There is no per-tool approval workflow or sandbox yet. MCP server commands run on your machine and tools can access or modify resources. Configure only trusted servers, use limited permissions, and avoid sensitive data. Prompt and tool results are sent to the Anthropic API. Task history is stored locally in `~/.clawd`.

## Not yet implemented
Animated transparent desktop pet, approval prompts/permissions UI, cancellation and queue, native tray and notifications, subscription usage meter, installers and extensive tests.

## License
MIT
