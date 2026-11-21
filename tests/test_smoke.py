import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ProjectSmokeTests(unittest.TestCase):
    def test_main_file_compiles(self):
        source = (ROOT / "clawd.py").read_text(encoding="utf-8")
        compile(source, "clawd.py", "exec")

    def test_example_mcp_config_is_valid_and_disabled(self):
        config = json.loads((ROOT / "mcp_servers.example.json").read_text(encoding="utf-8"))
        self.assertIsInstance(config.get("servers"), list)
        for server in config["servers"]:
            self.assertIn("name", server)
            self.assertIn("command", server)
            self.assertFalse(server.get("enabled", False), "Example MCP servers should be disabled by default")

if __name__ == "__main__":
    unittest.main()
