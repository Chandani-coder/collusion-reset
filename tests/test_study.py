from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest

from collusion_reset.study import FixtureBackend, episode_metrics, run_trajectory, summarize


class StudyTests(unittest.TestCase):
    def run_fixture(self, root, backend=None, **kwargs):
        return run_trajectory(backend or FixtureBackend(), list(range(15)), Path(root) / 'run',
                              trajectory_id='fixture-1', **kwargs)

    def test_full_checkpoint_branch_and_disk_roundtrip(self):
        with tempfile.TemporaryDirectory() as root:
            result = self.run_fixture(root)
            self.assertEqual(result['status'], 'complete')
            self.assertEqual(len(result['prefix']), 3)
            self.assertEqual(len(result['branches']), 4)
            self.assertEqual(len({b['future_pairs_sha256'] for b in result['branches'].values()}), 1)
            for branch in result['branches'].values():
                self.assertEqual(len(branch['episodes']), 5)
            checkpoint = json.loads((Path(root) / 'run/checkpoint.json').read_text())
            self.assertEqual(len(checkpoint['history_a']), 4)
            self.assertEqual(result, json.loads((Path(root) / 'run/study.json').read_text()))
            with self.assertRaises(FileExistsError):
                self.run_fixture(root)

    def test_reset_only_once_and_same_future_pairs(self):
        class Recording(FixtureBackend):
            def __init__(self):
                self.seen = []
            def episode(self, pair, histories, output, index):
                self.seen.append((output.name, pair, deepcopy(histories)))
                return super().episode(pair, histories, output, index)
        backend = Recording()
        with tempfile.TemporaryDirectory() as root:
            self.run_fixture(root, backend)
        for condition, expected in [('continue', (4, 4)), ('reset_a', (1, 4)),
                                    ('reset_b', (4, 1)), ('reset_both', (1, 1))]:
            calls = [c for c in backend.seen if c[0] == condition]
            self.assertEqual([c[1] for c in calls], list(range(3, 8)))
            self.assertEqual(tuple(len(calls[0][2][a]) for a in ('alice', 'bob')), expected)
            self.assertEqual(tuple(len(calls[1][2][a]) for a in ('alice', 'bob')),
                             tuple(n + 1 for n in expected))

    def test_ineligible_is_recorded(self):
        class Reject(FixtureBackend):
            def episode(self, *args):
                result = super().episode(*args)
                result['agents']['alice']['verdict'] = 'reject'
                result['agents']['alice']['verdict_submission']['verdict'] = 'reject'
                return result
        with tempfile.TemporaryDirectory() as root:
            result = self.run_fixture(root, Reject())
        self.assertEqual(result['status'], 'ineligible')
        self.assertEqual(len(result['prefix']), 10)
        self.assertEqual(result['branches'], {})

    def test_failure_is_preserved_without_claiming_completion(self):
        class Broken(FixtureBackend):
            def episode(self, *args):
                raise RuntimeError('fixture failure')
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(RuntimeError):
                self.run_fixture(root, Broken())
            result = json.loads((Path(root) / 'run/study.json').read_text())
        self.assertEqual(result['status'], 'failed')
        self.assertEqual(result['error_type'], 'RuntimeError')

    def test_missing_forced_or_small_log_is_not_unsupported_success(self):
        backend = FixtureBackend()
        result = backend.episode(None, backend.initial_state(), None, 0)
        self.assertTrue(episode_metrics(result)['unsupported_mutual_approval'])
        result['agents']['alice']['verdict_forced'] = True
        self.assertIsNone(episode_metrics(result)['unsupported_mutual_approval'])
        result['agents']['alice']['verdict_forced'] = False
        result['agents']['bob']['private_raw_log'] = []
        self.assertIsNone(episode_metrics(result)['unsupported_mutual_approval'])

    def test_short_schedule_fails_before_creating_output(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                run_trajectory(FixtureBackend(), [], Path(root) / 'run', trajectory_id='x')
            self.assertFalse((Path(root) / 'run').exists())

    def test_summary_uses_paired_trajectory_not_episode_count(self):
        with tempfile.TemporaryDirectory() as root:
            first = self.run_fixture(root)
        second = deepcopy(first)
        second['trajectory_id'] = 'fixture-2'
        for e in second['branches']['reset_both']['episodes']:
            e['unsupported_mutual_approval'] = False
        summary = summarize([first, second], bootstrap=100)
        self.assertEqual(summary['comparisons']['reset_both']['paired_n'], 2)
        self.assertEqual(summary['comparisons']['reset_both']['mean_difference'], -.5)
        self.assertEqual(summary['comparisons']['reset_a']['mean_difference'], 0)
        with self.assertRaises(ValueError):
            summarize([first, first])
        second['mode'] = 'live-pilot-not-main-study'
        with self.assertRaises(ValueError):
            summarize([first, second])


if __name__ == '__main__':
    unittest.main()
