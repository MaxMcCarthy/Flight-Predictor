import datetime

"""
DEFINE LEAP YEAR
The year can be evenly divided by 4;
If the year can be evenly divided by 100, it is NOT a leap year, unless;
The year is also evenly divisible by 400. Then it is a leap year.
"""


def is_leap_year(year):
    year = int(year)
    is_leap = False
    if year % 4 == 0:
        if year % 100:
            if year % 400:
                is_leap = True
        else:
            is_leap = True
    return is_leap


# Define months
MONTHS = {
    '1': 31,
    '3': 31,
    '4': 30,
    '5': 31,
    '6': 30,
    '7': 31,
    '8': 31,
    '9': 30,
    '10': 31,
    '11': 30,
    '12': 31,
}


def get_days_in_month(month, year):
    """
    given a month and year, find the days in the given month
    accounting for leap year
    :param month:
    :param year:
    :return: the number of days in the month
    """

    if str(month) == '2':
        if is_leap_year(year):
            return 29
        else:
            return 28
    return MONTHS[str(month)]


def calc_act(year, month, day, sched_hour, sched_min, delay):
    """
    from the database parameters, find the delay
    :param year:
    :param month:
    :param day:
    :param sched_hour:
    :param sched_min:
    :param delay:
    :return:
    """

    days_in_month = get_days_in_month(month, year)

    import datetime
    time1 = datetime.datetime(year, month, day, sched_hour, sched_min)
    time1 += datetime.timedelta(minutes=delay)
    return time1.month, time1.day, time1.hour, time1.minute


def calc_window(year, month, day, window_size):
    """

    :param year:
    :param month:
    :param day:
    :return:
    """

    time = datetime.datetime(year, month, day)
    t_delta = datetime.timedelta(days=window_size)
    back = time - t_delta
    forward = time + t_delta
    return back.month, back.day, forward.month, forward.day
