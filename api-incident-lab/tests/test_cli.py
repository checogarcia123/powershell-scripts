import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from api_incident_lab.cli import main


class CommandLineTests(unittest.TestCase):
    def test_demo_writes_readable_sanitized_reports(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            code = main(["demo", "--scenario", "authentication", "--output-dir", directory])
            self.assertEqual(code, 0)
            root = Path(directory)
            report = json.loads((root / "authentication.json").read_text())
            markdown = (root / "authentication.md").read_text()
            self.assertEqual(report["mode"], "simulated")
            self.assertIn("Incident handover", markdown)
            self.assertNotIn("sk-demo-DO-NOT-USE", markdown)

    def test_unknown_scenario_fails_before_writing(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as error:
                main(["demo", "--scenario", "does-not-exist", "--output-dir", directory])
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_live_requires_explicit_model_and_credentials(self):
        with patch.dict("os.environ", {}, clear=True), patch("sys.stdin.isatty", return_value=False), redirect_stderr(io.StringIO()):
            for args in (["live"], ["live", "--model", "available-test-model"]):
                with self.assertRaises(SystemExit) as error:
                    main(args)
                self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
