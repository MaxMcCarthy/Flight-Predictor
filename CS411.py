import base64
from io import BytesIO

import io
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import sqlite3
from sqlite3 import Error
from matplotlib import pyplot as plt
from matplotlib.backends.backend_template import FigureCanvas
from Tools.tools import calc_window, calc_act, get_days_in_month
import numpy as np

app = Flask(__name__)

app.debug = True


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(e)
        return None


conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')


def generate_params():
    airline = request.form['airline'].upper()
    origin_airport = request.form['origin_airport'].upper()
    dest_airport = request.form['dest_airport'].upper()
    dept_date = request.form['dept_date']
    print('here')
    delay = int(request.form['delay'])
    print('there')
    delayed = 'delayed' in request.form

    print(dept_date)

    year = int(dept_date[0:4])
    month = int(dept_date[5:7])
    day = int(dept_date[8:10])
    sched_hour = int(dept_date[11:13])
    sched_minute = int(dept_date[14:])

    params = (airline, origin_airport, dest_airport, year, month, day, sched_hour, sched_minute, delay, delayed)

    return params


@app.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        cur = conn.cursor()
        user_name = request.form['username']
        pw = request.form['password']
        cur.execute('''SELECT * FROM user WHERE username=? AND password=?;''', (user_name, pw))
        row = cur.fetchone()
        if row:
            return redirect(url_for('add_flight', userId=row[0]))
        error = 'Invalid username or password. Please try again!'
        return render_template('login.html', error=error)


@app.route('/newUser', methods=['POST', 'GET'])
def create_user():
    cur = conn.cursor()
    if request.method == 'POST':
        user_name = request.form['username']
        pw = request.form['password']

        cur.execute('''INSERT INTO user (username, password)
                 VALUES (?, ?)''', (user_name, pw))
        # conn.commit()
        # cur.execute('''SELECT user_id FROM user WHERE username=? AND password=?;''', (user_name, pw))
        cur.execute('''CREATE TRIGGER after_insert AFTER INSERT ON user
                       BEGIN
                       SELECT user_id FROM user WHERE username=user_name AND password=pw;
                       END;''')
        conn.commit()
        rows = cur.fetchone()
        print(rows)
        return redirect(url_for('add_flight', userId=rows[0]))
    else:
        return render_template('create_user.html')


@app.route('/<userId>/addFlight', methods=['POST', 'GET'])
def add_flight(userId):
    cur = conn.cursor()
    if request.method == 'POST':

        sql = '''INSERT INTO flights (airline, origin, destination, year, month, day, sched_hour, sched_min, delay, delayed, user_id)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?)'''
        print('hello')
        params = generate_params() + (userId,)
        print(params)
        cur.execute(sql, params)
        conn.commit()
        print("HERE")
        return redirect(url_for('add_flight', userId=userId))

    cur.execute('''SELECT * FROM flights WHERE user_id=?;''', (userId,))
    rows = cur.fetchall()
    return render_template('add_flight.html', rows=rows, userId=userId)


@app.route('/<userId>/<flightId>/deleteFlight', methods=['POST', 'GET'])
def delete_flight(userId, flightId):
    cur = conn.cursor()
    sql = '''DELETE FROM flights WHERE user_id=? AND flight_id=?;'''
    params = (userId, flightId)
    cur.execute(sql, params)
    conn.commit()
    return redirect(url_for('add_flight', userId=userId))


@app.route('/<userId>/<flightId>/edit', methods=['POST', 'GET'])
def edit_flight(userId, flightId):
    cur = conn.cursor()
    if request.method == 'POST':
        sql = '''UPDATE flights
                 SET airline=?, origin=?, destination=?, year=?, month=?, day=?, sched_hour=?, sched_min=?, delay=?, delayed=?
                 WHERE flight_id=?;'''
        params = generate_params() + (flightId,)
        cur.execute(sql, params)
        conn.commit()
        return redirect(url_for('add_flight', userId=userId))
    else:
        sql_select = '''SELECT * FROM flights WHERE flight_id=?;'''
        params_select = (flightId,)
        cur.execute(sql_select, params_select)
        flight = cur.fetchone()
        return render_template('edit_flight.html', userId=userId, flightId=flightId, flight=flight)


@app.route('/search', methods=['POST', 'GET'])
def search_flight():
    res = None
    indicator = 0
    data = {}
    if request.method == 'POST':
        cur = conn.cursor()
        airline = request.form['airline'].upper()
        origin_airport = request.form['origin_airport'].upper()
        dept_date = request.form['dept_date']

        data = {'airline': airline, 'origin': origin_airport, 'date': dept_date}

        year = int(dept_date[0:4])
        month = int(dept_date[5:7])
        day = int(dept_date[8:10])
        sched_hour = int(dept_date[11:13])
        sched_minute = int(dept_date[14:])

        window = 4
        b_month, b_day, f_month, f_day = calc_window(year, month, day, window)

        if b_month == f_month:
            sql = '''SELECT *
                     FROM flights
                     WHERE origin = ?
                     AND airline = ?
                     AND month = ?
                     AND day > ?
                     AND day < ?
            '''
            params = (origin_airport, airline, b_month, b_day, f_day)

        else:
            sql = '''SELECT day, sched_hour, AVG(delay)
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
                     GROUP BY day, sched_hour'''
            params = (origin_airport, airline, b_month, b_day, origin_airport, airline, f_month, f_day)

        cur.execute(sql, params)
        res = cur.fetchall()

        # value = [0] * 24
        # counts = [0] * 24
        #
        # # res -> day, hour, delay
        # for line in res:
        #     day = line[6]
        #     hour = line[7]
        #     delay = line[9]
        #     value[hour] = delay


        indicator = 0

    return render_template('search_flight.html', results=res, p_val=indicator, data=data)


@app.route('/getFig/<origin>/<airline>/<date>')
def get_fig(origin, airline, date):
    cur = conn.cursor()

    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    sched_hour = int(date[11:13])
    sched_minute = int(date[14:])

    window = 4
    b_month, b_day, f_month, f_day = calc_window(year, month, day, window)

    if b_month == f_month:
        sql = '''SELECT sched_hour, AVG(delay)
                 FROM flights
                 WHERE origin = ?
                 AND airline = ?
                 AND month = ?
                 AND day > ?
                 AND day < ?
                 GROUP BY sched_hour
        '''
        params = (origin, airline, b_month, b_day, f_day)

    else:
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
        params = (origin, airline, b_month, b_day, origin, airline, f_month, f_day)

    cur.execute(sql, params)
    res = cur.fetchall()
    print(res)

    value = [0] * 24

    # res -> hour, delay
    for line in res:
        hour = line[0]
        delay = line[1]
        value[hour] = delay

    fig, ax = plt.subplots()
    ax.plot(list(range(24)), value)
    ax.set_ylabel('Minutes')
    ax.set_xlabel('Hour')
    title = "Average Delay By Hour At " + origin + " Flying " + airline
    ax.set_title(title)
    img = io.BytesIO()
    fig.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype="image/png")


@app.route('/getFig/<origin>/<date>')
def get_fig_2(origin, date):
    cur = conn.cursor()

    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    sched_hour = int(date[11:13])
    sched_minute = int(date[14:])

    airline = {}

    sql = '''SELECT airline, AVG(delay)
             FROM flights
             WHERE origin = ?
             AND month = ?
             AND day = ?
             GROUP BY airline, day
    '''
    params = (origin, month, day)
    cur.execute(sql, params)
    res = cur.fetchall()

    # res -> airline, delay
    for line in res:
        carrier = line[0]
        delay = line[1]
        airline[carrier] = delay

    fig, ax = plt.subplots()

    ax.bar(airline.keys(), airline.values())
    ax.set_ylabel('Minutes')
    ax.set_xlabel('Airline')
    title = "Average Delay By Airline At " + origin + ' On ' + str(month) + '/' + str(day)
    ax.set_title(title)
    img1 = io.BytesIO()
    fig.savefig(img1, format='png')
    img1.seek(0)

    return send_file(img1, mimetype="image/png")


@app.route('/getFig3/<origin>/<airline>/<date>')
def get_fig_3(origin, airline, date):
    cur = conn.cursor()

    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    sched_hour = int(date[11:13])
    sched_minute = int(date[14:])

    airline_dict = {}
    window = 4
    b_month, b_day, f_month, f_day = calc_window(year, month, day, window)

    if b_month == f_month:
        sql = '''SELECT day, AVG(delay)
                 FROM flights
                 WHERE origin = ?
                 AND airline = ?
                 AND month = ?
                 AND day > ?
                 AND day < ?
                 GROUP BY day
        '''
        params = (origin, airline, b_month, b_day, f_day)

    else:
        sql = '''SELECT day, AVG(delay)
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
                 GROUP BY day'''
        params = (origin, airline, b_month, b_day, origin, airline, f_month, f_day)

    cur.execute(sql, params)
    res = cur.fetchall()

    # res -> day, delay
    for line in res:
        day = str(line[0])
        delay = line[1]
        airline_dict[day] = delay

    fig, ax = plt.subplots()

    ax.bar(airline_dict.keys(), airline_dict.values())
    ax.set_ylabel('Minutes')
    ax.set_xlabel('Day')
    title = "Average Delay By Day At " + origin + ' flying ' + airline
    ax.set_title(title)
    img2 = io.BytesIO()
    fig.savefig(img2, format='png')
    img2.seek(0)

    return send_file(img2, mimetype="image/png")


if __name__ == '__main__':
    app.secret_key = 'secret key'
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    app.run()
