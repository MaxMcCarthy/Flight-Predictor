import unittest
from Tools import tools
from Tools.tools import calc_delay, get_days_in_month


class TestFindDelays(unittest.TestCase):
    """Test finding the dealy"""

    def test_leap_year(self):
        """
        make sure that all the leap years are accounted for
        :return:
        """
        leap_year_days = [1804,
1808,
1812,
1816,
1820,
1824,
1828,
1832,
1836,
1840,
1844,
1848,
1852,
1856,
1860,
1864,
1868,
1872,
1876,
1880,
1884,
1888,
1892,
1896,
1904,
1908,
1912,
1916,
1920,
1924,
1928,
1932,
1936,
1940,
1944,
1948,
1952,
1956,
1960,
1964,
1968,
1972,
1976,
1980,
1984,
1988,
1992,
1996,
2000,
2004,
2008,
2012,
2016,
2020,
2024,
2028,
2032,
2036,
2040,
2044,
2048,
2052,
2056,
2060,
2064,
2068,
2072,
2076,
2080,
2084,
2088,
2092,
2096,
2104,
2108,
2112,
2116,
2120,
2124,
2128,
2132,
2136,
2140,
2144,
2148,
2152,
2156,
2160,
2164,
2168,
2172,
2176,
2180,
2184,
2188,
2192,
2196]

        for year in leap_year_days:
            days = get_days_in_month('2',str(year))
            self.assertEquals(days, 29)

    def test_cal_delay(self):
        """Is the delay correct, even if times roll over"""
        year = 2016 # leap year
        month = 4
        day = 22
        sched_hour = 22
        sched_min = 29
        act_hour = 23
        act_min = 9

        # test minute rollover
        # plus rollover
        delay = calc_delay(year, month, day, sched_hour, sched_min, act_hour, act_min)
        self.assertEquals(delay, 40)
        # negative rollover
        act_hour = 21
        delay = calc_delay(year, month, day, sched_hour, sched_min, act_hour, act_min)
        self.assertEquals(delay, -80)

        # test hour rollover
        # plus rollover
        act_hour = 01
        delay = calc_delay(year, month, day, sched_hour, sched_min, act_hour, act_min)
        self.assertEquals(delay, 160)
        # negative rollover
        sched_hour = 1
        act_hour = 23
        delay = calc_delay(year, month, day, sched_hour, sched_min, act_hour, act_min)
        self.assertEquals(delay, -140)

        # test day rollover
        # plus rollover
        month = 2
        day = 28




if __name__ == '__main__':
    unittest.main()