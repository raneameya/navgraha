import unittest

import pandas as pd
import pandas.testing as tm
pd.set_option('display.precision', 10)

from tests.example_charts import *
from core.chart.chart_helpers import d1_swetest

charts_to_test = [
    example_chart1, example_chart2, example_chart3, example_chart4, 
    example_chart5, example_chart6, example_chart7, example_chart8, 
    example_chart9, example_chart10, example_chart11
]
tol = 1e-7

class TestCustomSWE(unittest.TestCase):

    def check_chart_positions(self, crt):
        swetest_df = d1_swetest(crt).placements[['Graha', 'Lon', 'Speed']]
        cfun_df = crt.rasi.placements[['Graha', 'Lon', 'Speed']]

        # Map the Graha names so they match exactly
        cfun_swetest_graha_map = {
            'Lagna': 'Lagna', 'Sun': 'Sūrya', 'Moon': 'Candra', 
            'Mercury': 'Budha', 'Venus': 'Śukra', 'Mars': 'Maṅgala', 
            'Jupiter': 'Guru', 'Saturn': 'Śani', 'Rahu (true)': 'Rāhu', 
            'Ketu (true)': 'Ketu'
        }
        swetest_df['Graha'] = swetest_df['Graha'].map(cfun_swetest_graha_map)

        # Filter cfun_df to only include Grahas that exist in swetest_df
        cfun_df = cfun_df[cfun_df['Graha'].isin(swetest_df['Graha'])]

        # Clean, sort, and isolate the columns you want to compare
        df1 = swetest_df.set_index('Graha').sort_index()[['Lon', 'Speed']]
        df2 = cfun_df.set_index('Graha').sort_index()[['Lon', 'Speed']]
        print(pd.merge(df1, df2, on = 'Graha'))
        # Assert equality within tolerance
        tm.assert_frame_equal(df1, df2, atol = tol, check_exact = False)

    def test_multiple_charts(self):
        for chart in charts_to_test:
            # subTest ensures that if chart1 fails, chart2 still gets tested
            with self.subTest(chart=chart):
                self.check_chart_positions(crt = chart)