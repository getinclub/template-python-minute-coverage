import unittest
from harness import run_report
from fixtures import incident

def row(a,m,n):
    return {'asset':a,'minute_start':m,'covered_seconds':n,'expected_seconds':60,'status':'HEALTHY' if n==60 else 'GAP'}

class CoverageTests(unittest.TestCase):
    def test_exact_output_types(self):
        for row in run_report(*incident()):
            for key in ("minute_start", "covered_seconds", "expected_seconds"):
                self.assertIs(type(row[key]), int)
            for key in ("asset", "status"):
                self.assertIs(type(row[key]), str)
    def test_incident(self):
        self.assertEqual(run_report(*incident()),[row('alpha',0,60),row('alpha',60,59),row('alpha',120,0),row('beta',0,0),row('beta',60,0),row('beta',120,0)])
    def test_invalid_assets(self):
        for a in (None,(),['a','a'],[''],[1],[True],['x'*101],['x'+str(i) for i in range(101)]):
            with self.subTest(a=a),self.assertRaises(ValueError):run_report(a,0,60,[])
    def test_invalid_window(self):
        for start,end in ((True,60),(0,False),(0.0,60),(-60,0),(1,60),(0,61),(60,0),(0,86460),(1999999980,2000000040)):
            with self.subTest(start=start,end=end),self.assertRaises(ValueError):run_report(['a'],start,end,[])
    def test_invalid_rows(self):
        for rows in (None,(),[[]],[('a',0)],[('a',0,1,2)],[(1,0,1)],[('a',0.0,1)],[('a',True,1)],[('a',0,True)],[('a',0,2)],[('a',0,'1')],[('a',2000000001,1)]):
            with self.subTest(rows=rows),self.assertRaises(ValueError):run_report(['a'],0,60,rows)
    def test_full_validation_even_empty_window(self):
        with self.assertRaises(ValueError):run_report([],0,0,[('a',0,2)])
    def test_observation_limit(self):
        with self.assertRaises(ValueError):run_report(['a'],0,60,[('a',0,1)]*100001)
    def test_independent_owned_results(self):
        assets=['a']; obs=[('a',0,1)]; before=(assets[:],obs[:]); x=run_report(assets,0,60,obs);x[0]['covered_seconds']=999
        self.assertEqual(run_report(assets,0,60,obs),[row('a',0,1)])
        self.assertEqual((assets,obs),before)
    def test_many_minutes(self):
        self.assertEqual(run_report(['a'],0,86400,[]),[row('a',i,0) for i in range(0,86400,60)])
    def test_many_assets(self):
        a=['asset'+str(i) for i in range(100)]
        self.assertEqual(run_report(a,0,60,[]),[row(x,0,0) for x in sorted(a)])
    def test_case_00(self):
        self.assertEqual(run_report(['a'],0,60,[]),[row(*x) for x in [('a', 0, 0)]])
    def test_case_01(self):
        self.assertEqual(run_report([],0,60,[('a', 0, 1)]),[row(*x) for x in []])
    def test_case_02(self):
        self.assertEqual(run_report(['a'],0,0,[('a', 0, 1)]),[row(*x) for x in []])
    def test_case_03(self):
        self.assertEqual(run_report(['a'],60,60,[]),[row(*x) for x in []])
    def test_case_04(self):
        self.assertEqual(run_report(['a'],0,60,[('a', 0, 1)]),[row(*x) for x in [('a', 0, 1)]])
    def test_case_05(self):
        self.assertEqual(run_report(['a'],0,60,[('a', 59, 1)]),[row(*x) for x in [('a', 0, 1)]])
    def test_case_06(self):
        self.assertEqual(run_report(['a'],0,60,[('a', 60, 1)]),[row(*x) for x in [('a', 0, 0)]])
    def test_case_07(self):
        self.assertEqual(run_report(['a'],60,120,[('a', 59, 1), ('a', 60, 1), ('a', 119, 1), ('a', 120, 1)]),[row(*x) for x in [('a', 60, 2)]])
    def test_case_08(self):
        self.assertEqual(run_report(['a'],0,60,[('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1), ('a', 0, 1)]),[row(*x) for x in [('a', 0, 1)]])
    def test_case_09(self):
        self.assertEqual(run_report(['a'],0,60,[('a', 0, 1), ('a', 1, 1), ('a', 2, 1), ('a', 3, 1), ('a', 4, 1), ('a', 5, 1), ('a', 6, 1), ('a', 7, 1), ('a', 8, 1), ('a', 9, 1), ('a', 10, 1), ('a', 11, 1), ('a', 12, 1), ('a', 13, 1), ('a', 14, 1), ('a', 15, 1), ('a', 16, 1), ('a', 17, 1), ('a', 18, 1), ('a', 19, 1), ('a', 20, 1), ('a', 21, 1), ('a', 22, 1), ('a', 23, 1), ('a', 24, 1), ('a', 25, 1), ('a', 26, 1), ('a', 27, 1), ('a', 28, 1), ('a', 29, 1), ('a', 30, 1), ('a', 31, 1), ('a', 32, 1), ('a', 33, 1), ('a', 34, 1), ('a', 35, 1), ('a', 36, 1), ('a', 37, 1), ('a', 38, 1), ('a', 39, 1), ('a', 40, 1), ('a', 41, 1), ('a', 42, 1), ('a', 43, 1), ('a', 44, 1), ('a', 45, 1), ('a', 46, 1), ('a', 47, 1), ('a', 48, 1), ('a', 49, 1), ('a', 50, 1), ('a', 51, 1), ('a', 52, 1), ('a', 53, 1), ('a', 54, 1), ('a', 55, 1), ('a', 56, 1), ('a', 57, 1), ('a', 58, 1), ('a', 0, 1)]),[row(*x) for x in [('a', 0, 59)]])
    def test_case_10(self):
        self.assertEqual(run_report(['a'],0,60,[('a', 0, 1), ('a', 1, 1), ('a', 2, 1), ('a', 3, 1), ('a', 4, 1), ('a', 5, 1), ('a', 6, 1), ('a', 7, 1), ('a', 8, 1), ('a', 9, 1), ('a', 10, 1), ('a', 11, 1), ('a', 12, 1), ('a', 13, 1), ('a', 14, 1), ('a', 15, 1), ('a', 16, 1), ('a', 17, 1), ('a', 18, 1), ('a', 19, 1), ('a', 20, 1), ('a', 21, 1), ('a', 22, 1), ('a', 23, 1), ('a', 24, 1), ('a', 25, 1), ('a', 26, 1), ('a', 27, 1), ('a', 28, 1), ('a', 29, 1), ('a', 30, 1), ('a', 31, 1), ('a', 32, 1), ('a', 33, 1), ('a', 34, 1), ('a', 35, 1), ('a', 36, 1), ('a', 37, 1), ('a', 38, 1), ('a', 39, 1), ('a', 40, 1), ('a', 41, 1), ('a', 42, 1), ('a', 43, 1), ('a', 44, 1), ('a', 45, 1), ('a', 46, 1), ('a', 47, 1), ('a', 48, 1), ('a', 49, 1), ('a', 50, 1), ('a', 51, 1), ('a', 52, 1), ('a', 53, 1), ('a', 54, 1), ('a', 55, 1), ('a', 56, 1), ('a', 57, 1), ('a', 58, 1), ('a', 59, 1)]),[row(*x) for x in [('a', 0, 60)]])
    def test_case_11(self):
        self.assertEqual(run_report(['a'],0,60,[('a', 0, 0), ('a', 0, 1)]),[row(*x) for x in [('a', 0, 1)]])
    def test_case_12(self):
        self.assertEqual(run_report(['a'],0,60,[('a', 0, 0), ('a', 1, 0), ('a', 2, 0), ('a', 3, 0), ('a', 4, 0), ('a', 5, 0), ('a', 6, 0), ('a', 7, 0), ('a', 8, 0), ('a', 9, 0), ('a', 10, 0), ('a', 11, 0), ('a', 12, 0), ('a', 13, 0), ('a', 14, 0), ('a', 15, 0), ('a', 16, 0), ('a', 17, 0), ('a', 18, 0), ('a', 19, 0), ('a', 20, 0), ('a', 21, 0), ('a', 22, 0), ('a', 23, 0), ('a', 24, 0), ('a', 25, 0), ('a', 26, 0), ('a', 27, 0), ('a', 28, 0), ('a', 29, 0), ('a', 30, 0), ('a', 31, 0), ('a', 32, 0), ('a', 33, 0), ('a', 34, 0), ('a', 35, 0), ('a', 36, 0), ('a', 37, 0), ('a', 38, 0), ('a', 39, 0), ('a', 40, 0), ('a', 41, 0), ('a', 42, 0), ('a', 43, 0), ('a', 44, 0), ('a', 45, 0), ('a', 46, 0), ('a', 47, 0), ('a', 48, 0), ('a', 49, 0), ('a', 50, 0), ('a', 51, 0), ('a', 52, 0), ('a', 53, 0), ('a', 54, 0), ('a', 55, 0), ('a', 56, 0), ('a', 57, 0), ('a', 58, 0), ('a', 59, 0)]),[row(*x) for x in [('a', 0, 0)]])
    def test_case_13(self):
        self.assertEqual(run_report(['a'],0,60,[(None, 0, 1), ('a', None, 1), ('a', 0, None)]),[row(*x) for x in [('a', 0, 0)]])
    def test_case_14(self):
        self.assertEqual(run_report(['a'],0,60,[('ghost', 0, 1), ('ghost', 1, 1), ('ghost', 2, 1), ('ghost', 3, 1), ('ghost', 4, 1), ('ghost', 5, 1), ('ghost', 6, 1), ('ghost', 7, 1), ('ghost', 8, 1), ('ghost', 9, 1), ('ghost', 10, 1), ('ghost', 11, 1), ('ghost', 12, 1), ('ghost', 13, 1), ('ghost', 14, 1), ('ghost', 15, 1), ('ghost', 16, 1), ('ghost', 17, 1), ('ghost', 18, 1), ('ghost', 19, 1), ('ghost', 20, 1), ('ghost', 21, 1), ('ghost', 22, 1), ('ghost', 23, 1), ('ghost', 24, 1), ('ghost', 25, 1), ('ghost', 26, 1), ('ghost', 27, 1), ('ghost', 28, 1), ('ghost', 29, 1), ('ghost', 30, 1), ('ghost', 31, 1), ('ghost', 32, 1), ('ghost', 33, 1), ('ghost', 34, 1), ('ghost', 35, 1), ('ghost', 36, 1), ('ghost', 37, 1), ('ghost', 38, 1), ('ghost', 39, 1), ('ghost', 40, 1), ('ghost', 41, 1), ('ghost', 42, 1), ('ghost', 43, 1), ('ghost', 44, 1), ('ghost', 45, 1), ('ghost', 46, 1), ('ghost', 47, 1), ('ghost', 48, 1), ('ghost', 49, 1), ('ghost', 50, 1), ('ghost', 51, 1), ('ghost', 52, 1), ('ghost', 53, 1), ('ghost', 54, 1), ('ghost', 55, 1), ('ghost', 56, 1), ('ghost', 57, 1), ('ghost', 58, 1), ('ghost', 59, 1)]),[row(*x) for x in [('a', 0, 0)]])
    def test_case_15(self):
        self.assertEqual(run_report(['a', 'b'],0,60,[('a', 0, 1), ('b', 0, 1)]),[row(*x) for x in [('a', 0, 1), ('b', 0, 1)]])
    def test_case_16(self):
        self.assertEqual(run_report(['b', 'a'],120,240,[('b', 180, 1)]),[row(*x) for x in [('a', 120, 0), ('a', 180, 0), ('b', 120, 0), ('b', 180, 1)]])
    def test_case_17(self):
        self.assertEqual(run_report(['A', 'a', ' a'],0,60,[('a', 1, 1)]),[row(*x) for x in [(' a', 0, 0), ('A', 0, 0), ('a', 0, 1)]])
    def test_case_18(self):
        self.assertEqual(run_report(['é', '🙂'],0,60,[('é', 1, 1)]),[row(*x) for x in [('é', 0, 1), ('🙂', 0, 0)]])
    def test_case_19(self):
        self.assertEqual(run_report(['a'],0,60,[('a', -1, 1), ('a', 2000000000, 1)]),[row(*x) for x in [('a', 0, 0)]])
    def test_case_20(self):
        self.assertEqual(run_report(['a'],60,180,[('a', 60, 1), ('a', 120, 1)]),[row(*x) for x in [('a', 60, 1), ('a', 120, 1)]])
    def test_case_21(self):
        self.assertEqual(run_report(['a'],1999999920,1999999980,[('a', 1999999979, 1), ('a', 1999999980, 1)]),[row(*x) for x in [('a', 1999999920, 1)]])

if __name__=="__main__":unittest.main()
