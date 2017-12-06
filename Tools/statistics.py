import numpy as np
import pandas as pd
import sqlite3
from sqlite3 import Error
import statsmodels.formula.api as sm
import datetime
#from CS411 import create_connection


def hour_to_factor(x):
    """
    turn minutes from 0-59 into factors 1,2,3, or 4
    :param x: minute variable
    :return: the factor variable
    """
    if x < 15:
        return '<15'
    if x < 30:
        return '15<x<30'
    if x < 45:
        return '30<x<45'
    return '45<x<60'


def eliminate_zero(x):
    if x == 0:
        return 1
    return x


def day_of_week(x):
    if x == 0:
        return 'Sun'
    if x == 1:
        return 'Mon'
    if x == 2:
        return 'Tue'
    if x == 3:
        return 'Wed'
    if x == 4:
        return 'Thr'
    if x == 5:
        return 'Fri'
    if x == 6:
        return 'Sat'


def ret_month(x):
    if x == 1:
        return 'Jan'
    if x == 2:
        return 'Feb'
    if x == 3:
        return 'Mar'
    if x == 4:
        return 'Apr'
    if x == 5:
        return 'May'
    if x == 6:
        return 'Jun'
    if x == 7:
        return 'Jly'
    if x == 8:
        return 'Aug'
    if x == 9:
        return 'Sep'
    if x == 10:
        return 'Oct'
    if x == 11:
        return 'Nov'
    return 'Dec'


def create_data_frame(conn):
    """
    accesses database and formulates data for modeling
    :param conn:
    :return: a dataframe
    """

    # select data
    sql = '''
          SELECT airline, year, month, day, sched_hour, sched_min, delay
          FROM flights
          '''
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()

    # create dataframe
    df = pd.DataFrame(data, columns=['airline', 'year', 'month', 'day', 'hour', 'min', 'delay'])

    # take every nth observation for ease
    df = df.iloc[::100, :]

    # make minutes into factor
    df['min_cat'] = df['min'].apply(hour_to_factor)

    # change day of month to weekday
    df['weekday'] = df.apply(lambda row: datetime.datetime(row['year'], row['month'], row['day']).weekday(), axis=1)
    df['weekday'] = df['weekday'].apply(day_of_week)

    # remove 0s in delay
    #df['delay'] = df['delay'].apply(eliminate_zero)

    # change month to factor variable
    df['month'] = df['month'].apply(ret_month)

    # drop day and year from the dataframe
    df = df.drop(['day', 'year'], axis=1)

    print("made data!")
    return df


def permute_data(df, x, y):
    """

    :param df:
    :param x:
    :param y:
    :return:
    """

    # size of the dataframe
    lst = list(range(len(df['delay'])))

    # true difference of the means
    true_diff = np.mean(x['delay']) - np.mean(y['delay'])

    # number of repetitions
    m = 1000

    # length of the y vector
    n = len(y['delay'])

    diffs = np.zeros(m)

    # scramble x and y, then take the mean
    for i in range(m):
        samples = np.random.choice(lst, n, replace=False)
        x_s = df.iloc[samples]
        y_s = df.iloc[~samples]
        diffs[i] = (np.mean(x_s['delay']) - np.mean(y_s['delay']))

    # calculate how many of the means were greater than the true mean
    p_val = np.sum(diffs >= true_diff)/float(m)
    print(p_val)
    return p_val


def permute_factors(conn):
    #conn = create_connection('../flights.db')
    df = create_data_frame(conn)

    # hours
    factors = list(range(1,24))
    m = len(factors)
    num = (m * (m-1))/2
    p_vals = np.zeros(num)
    count = 0

    for i in range(m-1):
        for j in range(i+1,m):
            a = df.loc[df['hour'] == factors[i]]
            if len(a['delay']) == 0:
                continue
            b = df.loc[df['hour'] == factors[j]]
            if len(b['delay']) == 0:
                continue
            frames = [a,b]
            result = pd.concat(frames)
            p_val = permute_data(result, a, b)
            print(p_val)
            p_vals[count] = p_val
            count += 1
    print(p_vals)

    # month
    factors = list(range(1, 13))
    m = len(factors)
    num = (m * (m-1))/2
    p_vals = np.zeros(num)
    count = 0

    for i in range(m-1):
        for j in range(i+1,m):
            a = df.loc[df['month'] == factors[i]]
            if len(a['delay']) == 0:
                continue
            b = df.loc[df['month'] == factors[j]]
            if len(b['delay']) == 0:
                continue
            frames = [a,b]
            result = pd.concat(frames)
            p_val = permute_data(result, a, b)
            p_vals[count] = p_val
            count += 1
    print(p_vals)

    # day
    factors = list(range(1, 32))
    m = len(factors)
    num = (m * (m-1))/2
    p_vals = np.zeros(num)
    count = 0

    for i in range(m-1):
        for j in range(i+1,m):
            a = df.loc[df['weekday'] == factors[i]]
            if len(a['delay']) == 0:
                continue
            b = df.loc[df['weekday'] == factors[j]]
            if len(b['delay']) == 0:
                continue
            frames = [a,b]
            result = pd.concat(frames)
            p_val = permute_data(result, a, b)
            p_vals[count] = p_val
            count += 1
    print(p_vals)

    # minutes
    factors = list(range(0, 60))
    m = len(factors)
    num = (m * (m-1))/2
    p_vals = np.zeros(num)
    count = 0

    for i in range(m-1):
        for j in range(i+1,m):
            a = df.loc[df['min'] == factors[i]]
            if len(a['delay']) == 0:
                continue
            b = df.loc[df['min'] == factors[j]]
            if len(b['delay']) == 0:
                continue
            frames = [a,b]
            result = pd.concat(frames)
            p_val = permute_data(result, a, b)
            print(p_val)
            p_vals[count] = p_val
            count += 1
    print(p_vals)

    # airline
    factors = df.airline.unique()
    m = len(factors)
    num = (m * (m-1))/2
    p_vals = np.zeros(num)
    count = 0

    for i in range(m-1):
        for j in range(i+1,m):
            a = df.loc[df['min_cat'] == factors[i]]
            if len(a['delay']) == 0:
                continue
            b = df.loc[df['min_cat'] == factors[j]]
            if len(b['delay']) == 0:
                continue
            frames = [a,b]
            result = pd.concat(frames)
            p_val = permute_data(result, a, b)
            print(p_val)
            p_vals[count] = p_val
            count += 1
    print(p_vals)


def create_model(conn):
    #conn = create_connection('../test.db')
    df = create_data_frame(conn)
    result = sm.ols(formula="delay ~ min_cat + hour + airline + weekday + month", data=df).fit()
    m1 = sm.ols(formula="delay ~ min_cat + hour + airline + weekday + month", data=df).fit()
    print(m1.params)
    print(m1.summary())
    point = df.iloc[[100]]
    curr_delay = point.iloc[[0]]['delay']
    point = point.drop(['delay'], axis=1)
    print(np.square(m1.predict(point) - curr_delay))


def calc_wait_time(conn, month, day, hour, minute, year, airline):
    df = create_data_frame(conn)
    result = sm.ols(formula="delay ~ min_cat + hour + airline + weekday + month", data=df).fit()
    data = (airline, ret_month(month), day_of_week(datetime.datetime(year, month, day).weekday()), hour, hour_to_factor(minute))
    print(data)
    point = pd.DataFrame([data], columns=['airline', 'month', 'weekday', 'hour', 'min_cat'])
    return result.predict(point)


def cross_validation(df):
    # length of the dataframe
    n = len(df['delay'])

    # error vectors
    e1 = np.zeros(n)
    e2 = np.zeros(n)
    e3 = np.zeros(n)

    # get factors for factor variables
    min_cats = df['min_cat'].unique()
    hours = df['hour'].unique()
    airlines = df['airline'].unique()
    weekdays = df['weekday'].unique()
    months = df['month'].unique()

    # leave one out cross validation
    # set one test point, the rest are training points
    # measure model's accuracy predicting known test point
    # store in e for error
    for i in range(n):
        sample_df = df.iloc[[~i]]
        point = df.iloc[[i]]
        curr_delay = point.iloc[[0]]['delay']
        point = point.drop(['delay'], axis=1)

        m1 = sm.ols(formula="delay ~ C(min_cat, levels=min_cats) + "
                            "C(hour, levels=hours) + "
                            "C(weekday, levels=weekdays) + "
                            "C(month, levels=months) + "
                            "C(airline, levels=airlines)",
                            data=sample_df).fit()
        e1[i] = np.square(m1.predict(point) - curr_delay)

        m2 = sm.ols(formula="delay ~ C(min_cat, levels=min_cats) + "
                            "C(hour, levels=hours) + "
                            "C(airline, levels=airlines) + "
                            "C(weekday, levels=weekdays)",
                            data=sample_df).fit()
        e2[i] = np.square(m2.predict(point) - curr_delay)

        m3 = sm.ols(formula="delay ~ C(min_cat, levels=min_cats) + "
                            "C(hour, levels=hours) + "
                            "C(airline, levels=airlines) + "
                            "C(month, levels=months)",
                            data=sample_df).fit()
        e3[i] = np.square(m3.predict(point) - curr_delay)

        if i % 500 == 0:
            print(i//500)

    err1 = np.mean(e1)
    err2 = np.mean(e2)
    err3 = np.mean(e3)
    print(err1, err2, err3)

    return err1, err2, err3


if __name__ == '__main__':
    #conn = create_connection('/Users/Max/PycharmProjects/Flight-Predictor/flights.db')
    #conn = create_connection('../test.db')
    #create_data_frame(conn)
    #permute_factors()
    #create_model()
    #df = create_data_frame(conn)
    #cross_validation(df)
    #print(calc_wait_time(conn, 4, 23, 15, 37, 2017, 'DL'))
    print()
