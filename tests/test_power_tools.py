import csv
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'power_analysis' / 'joint_from_marginals.py'
spec = importlib.util.spec_from_file_location('joint_from_marginals', SCRIPT)
joint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(joint)

class TestPowerCalculations(unittest.TestCase):
    def _data(self):
        with joint.INPUT.open(newline='', encoding='utf-8') as f:
            return joint.compute(list(csv.DictReader(f)))

    def test_paper_approximations(self):
        rows = self._data()
        indexed = {(int(r['prompt_pairs']),float(r['tau']),r['EA_scenario'],r['RF_scenario']):r for r in rows}
        self.assertAlmostEqual(indexed[(60,0.5,'EA_OR2','RF_OR1_vs_2/3')]['product_independence_approx'],0.91)
        self.assertAlmostEqual(indexed[(60,0.5,'EA_OR1.5','RF_OR1_vs_2/3')]['product_independence_approx'],0.7735)

    def test_scenario_grid_complete(self):
        rows = self._data()
        self.assertEqual(len(rows), 3*2*2*2)
        self.assertTrue(all(0 <= float(row['product_independence_approx']) <= 1 for row in rows))
        self.assertTrue(all(row['status'].endswith('NOT_direct_joint') for row in rows))

if __name__ == '__main__':
    unittest.main()
