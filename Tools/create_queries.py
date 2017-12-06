import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(e)
        return None


def aggregate():
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    cur = conn.cursor()
    sql = '''SELECT airline, sched_hour, AVG(delay)
             FROM flights
             WHERE airline='AA'
             GROUP BY sched_hour
        '''
    params = ()
    cur.execute(sql, params)
    print(cur.fetchall())


def make_view():
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    cur = conn.cursor()
    sql = '''CREATE VIEW IF NOT EXISTS avg_waits AS
             SELECT airport, month, day, hour, AVG(avg_wait) AS avg_wait, AVG(max_wait) as avg_max_wait
             FROM wait_time
             GROUP BY airport, month, day, hour;
          '''
    cur.execute(sql)
    conn.commit()
    sql = '''SELECT * FROM avg_waits'''
    cur.execute(sql)
    print(cur.fetchall())


def find_wait_time():
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    cur = conn.cursor()

    sql = '''SELECT f.origin, f.year, f.month, f.day, f.sched_hour, f.sched_min, f.delay, f.delayed, f.user_id, w.avg_wait, w.avg_max_wait
             FROM flights as f
             JOIN avg_waits as w
             ON f.origin = w.airport AND f.month = w.month AND f.day = w.day AND f.sched_hour = w.hour
             WHERE f.origin = ?
             AND f.month = ?
             AND f.day = ?
             AND f.sched_hour = ?
    '''
    params = ('JFK', 1,1,6)
    cur.execute(sql, params)
    print(cur.fetchall())


def find_delay_hour():
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    cur = conn.cursor()
    sql = '''SELECT day, sched_hour, AVG(delay)
             FROM flights
             WHERE origin = ?
             AND airline = ?
             AND month = ?
             AND day > ?
             AND day < ?
             GROUP BY day, sched_hour
    '''
    params = ('ATL', 'DL', 1, 4, 6)
    cur.execute(sql, params)
    res = cur.fetchall()
    print(res)
    print(len(res))

    sql = '''SELECT sched_hour, AVG(delay)
             FROM (
                 SELECT *
                 FROM flights
                 WHERE origin=?
                 AND airline=?
                 AND month=?
                 AND day>?
                 UNION
                 SELECT *
                 FROM flights
                 WHERE origin=?
                 AND airline=?
                 AND month=?
                 AND day<?
             )
             GROUP BY sched_hour'''
    params = ('ATL', 'DL', 12, 27, 'ATL', 'DL', 1, 5)
    cur.execute(sql, params)
    res = cur.fetchall()
    print(res)
    print(len(res))


def find_delay_by_day():
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    cur = conn.cursor()
    sql = '''SELECT day, sched_hour, AVG(delay)
             FROM flights
             WHERE origin = ?
             AND airline = ?
             AND month = ?
             AND day > ?
             AND day < ?
             GROUP BY day
    '''
    params = ('ATL', 'DL', 1, 4, 10)
    cur.execute(sql, params)
    res = cur.fetchall()
    print(res)
    print(len(res))


def find_delay_by_airport():
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    cur = conn.cursor()
    sql = '''SELECT airline, AVG(delay)
             FROM flights
             WHERE origin = ?
             AND month = ?
             AND day > ?
             AND day < ?
             GROUP BY airline, day
    '''
    params = ('ORD', 1, 4, 6)
    cur.execute(sql, params)
    res = cur.fetchall()
    print(res)
    print(len(res))


def find_flights_in_a_day():
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    cur = conn.cursor()
    sql = '''SELECT day, PERCENTILE(delay)
             FROM flights
             WHERE origin = ?
             AND month = ?
             AND day = ?
             GROUP BY day
    '''
    params = ('ATL', 5, 9)
    cur.execute(sql, params)
    res = cur.fetchall()
    print(res)
    print(len(res))


if __name__ == '__main__':
    #aggregate()
    #make_view()
    #find_wait_time()
    #find_delay_hour()
    find_delay_by_airport()
    #find_delay_by_day()
    #find_flights_in_a_day()