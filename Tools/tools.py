

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


def calc_delay(year, month, day, sched_hour, sched_min, act_hour, act_min):
    """
    from the database parameters, find the delay
    :param year:
    :param month:
    :param day:
    :param sched_hour:
    :param sched_min:
    :param act_hour:
    :param act_min:
    :return:
    """

    days_in_month = get_days_in_month(month, year)

    import datetime
    time1 = datetime.datetime(year, month, day, sched_hour, sched_min)

    if sched_hour - act_hour > 2:
        day += 1

        if day > days_in_month:
            day = 1
            month += 1

            if month > 12:
                month = 1
                year += 1

    elif abs(sched_hour - act_hour) > 2:
        day -= 1

        if day < days_in_month:
            month -= 1
            if month < 1:
                month = 12
                year -= 1
            day = get_days_in_month(month, year)

    time2 = datetime.datetime(year, month, day, act_hour, act_min)

    if time1 < time2:
        time_delta = time2-time1
    else:
        time_delta = time1 - time2
        delay = time_delta.seconds/60
        return delay * -1

    delay = time_delta.seconds/60

    return delay