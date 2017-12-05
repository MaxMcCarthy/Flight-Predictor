import numpy as np
import pandas as pd
import sqlite3
from sqlite3 import Error
import statsmodels.formula.api as sm
import datetime


def hour_to_factor(x):
    if x < 15:
        return 1
    if x < 30:
        return 2
    if x < 45:
        return 3
    return 4


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


def create_data_frame(conn):
    """

    :param conn:
    :return:
    """

    sql = '''
          SELECT airline, origin, year, month, day, sched_hour, sched_min, delay
          FROM flights
          '''
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    df = pd.DataFrame(data, columns=['airline', 'origin', 'year', 'month', 'day', 'hour', 'min', 'delay'])
    df = df.iloc[::500, :]
    df['min_cat'] = df['min'].apply(hour_to_factor)
    df['weekday'] = df.apply(lambda row: datetime.datetime(row['year'], row['month'], row['day']).weekday(), axis=1)
    df['weekday'] = df['weekday'].apply(day_of_week)
    df = df.drop(['day', 'year'], axis=1)
    print("made data!")
    return df


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(e)
        return None


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

    for i in range(m):
        samples = np.random.choice(lst, n, replace=False)
        x_s = df.iloc[samples]
        y_s = df.iloc[~samples]
        diffs[i] = (np.mean(x_s['delay']) - np.mean(y_s['delay']))

    p_val = np.sum(diffs >= true_diff)/float(m)
    print(p_val)
    return p_val


def permute_factors():
    conn = create_connection('/Users/Max/PycharmProjects/Flight-Predictor/flights.db')
    df = create_data_frame(conn)

    # # hours
    # factors = list(range(1,24))
    # m = len(factors)
    # num = (m * (m-1))/2
    # p_vals = np.zeros(num)
    # count = 0
    #
    # for i in range(m-1):
    #     for j in range(i+1,m):
    #         a = df.loc[df['hour'] == factors[i]]
    #         if len(a['delay']) == 0:
    #             continue
    #         b = df.loc[df['hour'] == factors[j]]
    #         if len(b['delay']) == 0:
    #             continue
    #         frames = [a,b]
    #         result = pd.concat(frames)
    #         p_val = permute_data(result, a, b)
    #         print(p_val)
    #         p_vals[count] = p_val
    #         count += 1
    # print(p_vals)

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
            a = df.loc[df['day'] == factors[i]]
            if len(a['delay']) == 0:
                continue
            b = df.loc[df['day'] == factors[j]]
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


def create_model():
    conn = create_connection('/Users/Max/PycharmProjects/Flight-Predictor/flights.db')
    df = create_data_frame(conn)
    result = sm.ols(formula="delay ~ min_cat + hour + airline + weekday + month", data=df).fit()
    print(result.params)
    print(result.summary())


if __name__ == '__main__':
    #conn = create_connection('/Users/Max/PycharmProjects/Flight-Predictor/flights.db')
    #create_data_frame(conn)
    #permute_factors()
    create_model()
