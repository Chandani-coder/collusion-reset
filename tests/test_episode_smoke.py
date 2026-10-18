import tempfile
import unittest
from unittest.mock import patch

from collusion_reset.episode_smoke import MANIFEST, live_command, main, validate_pair


class EpisodeSmokeTests(unittest.TestCase):
    def test_real_tasks_and_upstream_grader(self):
        report = validate_pair()
        self.assertEqual(report["live_model_calls"], 0)
        self.assertEqual(report["agents"]["A"]["reference_row_count"], 8)
        self.assertEqual(report["agents"]["B"]["reference_row_count"], 8)
        for agent in report["agents"].values():
            self.assertTrue(all(agent["checks"].values()))

    def test_live_command_uses_one_pair_and_same_model(self):
        with tempfile.TemporaryDirectory() as output:
            command = live_command("openrouter/example/model:free", output)
        self.assertEqual(command[command.index("--manifest") + 1], str(MANIFEST))
        self.assertEqual(command[command.index("--alice-model") + 1],
                         command[command.index("--bob-model") + 1])
        self.assertIn("raw-only", command)

    def test_non_free_or_implicit_routes_are_rejected(self):
        for model in ("openai/example", "openrouter/example/model", ""):
            with self.assertRaises(ValueError):
                live_command(model, "results")

    def test_default_does_not_launch_live_runner(self):
        with patch("sys.argv", ["episode_smoke"]), patch("builtins.print"), \
                patch("collusion_reset.episode_smoke.validate_pair", return_value={}), \
                patch("collusion_reset.episode_smoke.subprocess.run") as run:
            main()
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
