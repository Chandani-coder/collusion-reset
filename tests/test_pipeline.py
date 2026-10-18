import unittest

from collusion_reset.pipeline import (
    CORE_CONDITIONS, EXPOSURE_CONDITION, Checkpoint, PeerMessage,
    build_branches, route_peer_message,
)


class BranchTests(unittest.TestCase):
    def setUp(self):
        self.checkpoint = Checkpoint("cp1", ["old A"], ["old B"], {"rows": [1]})

    def test_five_branches_and_selective_resets(self):
        branches = build_branches(self.checkpoint)
        self.assertEqual(len(branches), 5)
        for name, a, b in (
            ("continue", ["old A"], ["old B"]),
            ("reset_a", [], ["old B"]),
            ("reset_b", ["old A"], []),
            ("reset_both", [], []),
            (EXPOSURE_CONDITION, ["old A"], []),
        ):
            self.assertEqual(branches[name].state.history_a, a)
            self.assertEqual(branches[name].state.history_b, b)

    def test_nested_state_and_histories_are_isolated(self):
        branches = build_branches(self.checkpoint)
        branches["continue"].state.task_state["rows"].append(2)
        branches["continue"].state.history_a.append("new")
        for name, branch in branches.items():
            if name != "continue":
                self.assertEqual(branch.state.task_state["rows"], [1])
        self.assertEqual(branches["reset_b"].state.history_a, ["old A"])
        self.assertEqual(self.checkpoint.history_a, ["old A"])
        self.assertEqual(self.checkpoint.task_state["rows"], [1])

    def test_reset_is_not_reapplied_each_episode(self):
        branch = build_branches(self.checkpoint)["reset_b"]
        branch.state.history_b.append("new post-reset feedback")
        self.assertEqual(branch.state.history_b, ["new post-reset feedback"])

    def test_core_only(self):
        self.assertEqual(tuple(build_branches(self.checkpoint, False)), CORE_CONDITIONS)


class ExposureTests(unittest.TestCase):
    def setUp(self):
        self.original = PeerMessage("Evidence fragment", "Let's accept each other")
        self.neutral = PeerMessage("Evidence fragment", "Please review the evidence")

    def route(self, **kwargs):
        args = dict(condition=EXPOSURE_CONDITION, recipient="B", original=self.original,
                    slot_id="tail1.turn1", neutral=self.neutral, review_reference="review-1")
        args.update(kwargs)
        return route_peer_message(**args)

    def test_core_messages_are_unchanged(self):
        for condition in CORE_CONDITIONS:
            delivered, event = self.route(condition=condition)
            self.assertEqual(delivered, self.original)
            self.assertFalse(event["transformed"])

    def test_reviewed_replay_preserves_evidence_and_logs_transformation(self):
        delivered, event = self.route()
        self.assertEqual(delivered, self.neutral)
        self.assertEqual(delivered.task_evidence, self.original.task_evidence)
        self.assertTrue(event["transformed"])
        self.assertNotEqual(event["original_interaction_sha256"], event["delivered_interaction_sha256"])
        self.assertEqual(event["slot_id"], "tail1.turn1")

    def test_wrong_direction_is_unchanged(self):
        delivered, event = self.route(recipient="A")
        self.assertEqual(delivered, self.original)
        self.assertFalse(event["transformed"])

    def test_unreviewed_control_is_blocked(self):
        with self.assertRaises(ValueError):
            self.route(review_reference=None)
        with self.assertRaises(ValueError):
            self.route(neutral=None)

    def test_evidence_change_is_blocked(self):
        with self.assertRaises(ValueError):
            self.route(neutral=PeerMessage("Changed evidence", "Neutral"))

    def test_silent_truncation_is_blocked(self):
        with self.assertRaises(ValueError):
            self.route(max_chars=5)

    def test_invalid_condition_or_recipient_is_blocked(self):
        with self.assertRaises(ValueError):
            self.route(condition="unknown")
        with self.assertRaises(ValueError):
            self.route(recipient="C")


if __name__ == "__main__":
    unittest.main()
