# Security notes

This project is experimental. MCP server commands are launched as local subprocesses. Tool calls currently lack individual approval gates and sandboxing. Use only trusted servers with narrowly scoped permissions. Task prompts and tool outputs are sent to Anthropic's API and task history is persisted locally in ~/.clawd. Do not connect sensitive workspaces until safeguards improve.

Report security issues privately when possible.
