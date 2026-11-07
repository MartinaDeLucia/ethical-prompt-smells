import csv
import importlib.util
import pathlib
import tempfile
import unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
MOD=ROOT/'sampling'/'capped_sampling.py'
spec=importlib.util.spec_from_file_location('sampler',MOD)
sampler=importlib.util.module_from_spec(spec);spec.loader.exec_module(sampler)


def make_rows(counts):
    return [{'prompt_id':f'{s}_{i:04d}','smell':s} for s,n in counts.items() for i in range(n)]

class TestCappedSampling(unittest.TestCase):
    def test_minimal_cap_and_balance(self):
        counts={'EPS-01':25,'EPS-02':30,'EPS-03':12,'EPS-04':8,'EPS-05':5,'EPS-06':4,'EPS-07':10,'EPS-08':3}
        selected,d=sampler.select_pairs(make_rows(counts),N=60,seed=44)
        self.assertEqual(d['C'],10)
        self.assertEqual(d['total_selected'],60)
        self.assertFalse(d['sensitivity_analysis_required'])
        self.assertEqual(d['selected_by_smell']['EPS-02'],10)
    def test_overshoot_possible(self):
        counts={'EPS-01':10,'EPS-02':10}
        _,d=sampler.select_pairs(make_rows(counts),N=15)
        self.assertEqual(d['C'],8);self.assertEqual(d['total_selected'],16)
    def test_all_if_insufficient(self):
        selected,d=sampler.select_pairs(make_rows({'EPS-01':2,'EPS-03':1}),N=60)
        self.assertIsNone(d['C']);self.assertTrue(d['sensitivity_analysis_required']);self.assertEqual(len(selected),3)
        self.assertEqual(d['eligible_validated_by_smell']['EPS-08'],0)
    def test_determinism_order_independent(self):
        rows=make_rows({'EPS-01':8,'EPS-02':8})
        a,_=sampler.select_pairs(rows,N=10,seed=3)
        b,_=sampler.select_pairs(list(reversed(rows)),N=10,seed=3)
        self.assertEqual(a,b)
    def test_duplicate_and_bad_smell(self):
        with self.assertRaises(ValueError):
            sampler.select_pairs(make_rows({'EPS-01':1})*2,N=1)
        with self.assertRaises(ValueError):
            sampler.select_pairs([{'prompt_id':'X','smell':'EPS-09'}],N=1)
    def test_exact_N(self):
        rows=make_rows({'EPS-01':1,'EPS-08':1})
        _,d=sampler.select_pairs(rows,N=2)
        self.assertEqual(d['C'],1);self.assertEqual(d['total_selected'],2)

if __name__=='__main__': unittest.main()
