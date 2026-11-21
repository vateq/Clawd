import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ProjectSmokeTests(unittest.TestCase):
    def test_main_file_compiles(self):
        compile((ROOT / "clawd.py").read_text(encoding="utf-8"), "clawd.py", "exec")

    def test_example_config_is_valid_and_disabled(self):
        config = json.loads((ROOT / "mcp_servers.example.json").read_text(encoding="utf-8"))
        self.assertIsInstance(config.get("servers"), list)
        for server in config["servers"]:
            self.assertIn("name", server)
            self.assertIn("command", server)
            self.assertFalse(server.get("enabled", False))

    def test_build_scripts_exist(self):
        self.assertTrue((ROOT / "build_windows.bat").is_file())
        self.assertTrue((ROOT / "build_unix.sh").is_file())

if __name__ == "__main__":
    unittest.main()
