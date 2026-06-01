import unittest
import pandas as pd
from pandas.testing import assert_frame_equal

from tests.example_charts import *
from tests.process_lons import process_jh_lons, chart_vargas

class TestVargaCalculations(unittest.TestCase):

    def setUp(self):
        '''Map each imported chart object directly to its matching JHora file list.'''
        self.test_cases = [
            {
                'name': 'Example Chart 1',
                'chart_obj': example_chart1,
                'filenames': [
                    'example_1_jh_1.txt', 'example_1_jh_2.txt', 'example_1_jh_3.txt',
                    'example_1_jh_4.txt', 'example_1_jh_5.txt', 'example_1_jh_6.txt',
                    'example_1_jh_7.txt'
                ]
            },
            {
                'name': 'Example Chart 2',
                'chart_obj': example_chart2,
                'filenames': [
                    'example_2_jh_1.txt', 'example_2_jh_2.txt', 'example_2_jh_3.txt',
                    'example_2_jh_4.txt', 'example_2_jh_5.txt', 'example_2_jh_6.txt',
                    'example_2_jh_7.txt'
                ]
            }
        ]

    def test_all_charts_match_jhora(self):
        '''Validate all test charts against their JHora reference outputs.'''
        for case in self.test_cases:
            # The subtest context manager isolates failures per chart
            with self.subTest(chart = case['name']):
                # Get computed varga lons for charts
                actual_df = chart_vargas(case['chart_obj'])
                # Read in JHora varga lons
                jhora_df = process_jh_lons(paths = case['filenames'])
                # Filter both DataFrames using an inner merge against the shared keys
                shared_keys = pd.merge(
                    actual_df[['VargaJH', 'Graha']], 
                    jhora_df[['VargaJH', 'Graha']], 
                    on = ['VargaJH', 'Graha'], 
                    how = 'inner'
                )
                actual_df = pd.merge(
                    actual_df, shared_keys, on = ['VargaJH', 'Graha'], how = 'inner'
                )
                jhora_df = pd.merge(
                    jhora_df, shared_keys, on = ['VargaJH', 'Graha'], how = 'inner'
                )
                # Standardise sorting and row indices
                sort_columns = ['VargaJH', 'Graha']
                actual_sorted = (
                    actual_df.sort_values(by = sort_columns)
                    .reset_index(drop = True)
                )
                jhora_sorted = (
                    jhora_df.sort_values(by = sort_columns)
                    .reset_index(drop = True)
                )
                pd.merge(
                    actual_df, jhora_df, on = ['VargaJH', 'Graha'], 
                    suffixes = ['_act', '_jh']
                ).to_csv('merged' + case['name'] + '.csv')
                # Allow float tolerance
                assert_frame_equal(
                    actual_sorted,
                    jhora_sorted,
                    check_dtype = False,
                    atol = 2.6,
                    obj = f'Mismatched data detected in: {case['name']}'
                )

if __name__ == '__main__':
    unittest.main()
