# Clawd 🧡

A tiny desktop Claude companion: a friendly floating mascot, speech bubble, and background task runner.

> Early MVP: chat/task execution through the Anthropic API is implemented. MCP integrations and live subscription usage tracking are planned, not yet implemented.

## Features
- Floating desktop window with a mascot and speech bubble
- Submit a task and keep the UI responsive while Claude works
- Anthropic API integration
- Configurable model and API key via environment variables
- Optional manual usage-limit display (not connected to account usage data)

## Run
1. Install Python 3.10+.
2. `python -m pip install -r requirements.txt`
3. Set `ANTHROPIC_API_KEY` in your environment.
4. Run `python clawd.py`.

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

Set `ANTHROPIC_MODEL` to override the default model. Set `CLAWD_DAILY_REMAINING` and `CLAWD_WEEKLY_REMAINING` to show manually-entered usage text in the UI.

## Roadmap
- [ ] MCP client and server management
- [ ] Native desktop notifications and tray integration
- [ ] Animated mascot / idle states
- [ ] Accurate usage tracking where officially supported
- [ ] Task history and persistent queue
- [ ] Windows/macOS/Linux packaging

## Safety
Clawd currently sends task text to the Anthropic API. Don't enter secrets or sensitive data unless you are comfortable sending them to the API. The MVP does not execute shell commands or access your files.

## License
MIT. See [LICENSE](LICENSE).
