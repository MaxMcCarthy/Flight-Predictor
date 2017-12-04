import base64
from StringIO import StringIO
from io import BytesIO

import io
from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
from sqlite3 import Error
from matplotlib import pyplot as plt
from matplotlib.backends.backend_template import FigureCanvas
from Tools.tools import calc_delay, get_days_in_month
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
    airline = request.form['airline']
    origin_airport = request.form['origin_airport']
    dest_airport = request.form['dest_airport']
    dept_date = request.form['dept_date']
    act_dept = request.form['act_dept']
    delayed = 'delayed' in request.form

    print(dept_date)

    year = int(dept_date[0:4])
    month = int(dept_date[5:7])
    day = int(dept_date[8:10])
    sched_hour = int(dept_date[11:13])
    sched_minute = int(dept_date[14:])

    act_hour = int(act_dept[:2])
    act_min = int(act_dept[3:])

    params = (airline, origin_airport, dest_airport, year, month, day, sched_hour, sched_minute, act_hour, act_min, delayed)

    return params


def get_flights_in_window(window, day, month, year, origin, airline=None):
    """

    :param window:
    :param day:
    :param month:
    :param year:
    :param origin:
    :param airline:
    :return:
    """

    cur = conn.cursor()

    if window > 13:
        window = 13

    num_days = get_days_in_month(month, year)

    if day+window > num_days or day-window < 0:

        if day + window > num_days:
            start_day = day - window
            start_month = month
            end_month = month + 1
            if end_month > 12:
                end_month = 1
            end_day = (day+window) - num_days

        else:
            start_month = month - 1
            if start_month < 1:
                start_month = 12
            start_day = (day-window) + get_days_in_month(start_month, year)
            end_month = month
            end_day = day + window

        params, sql = select_query_complex(airline, end_day, end_month, origin, start_day, start_month)

    else:
        params, sql = method_name(airline, day, month, origin, window)
    print(params)
    cur.execute(sql, params)
    return cur.fetchall()


def method_name(airline, day, month, origin, window):
    if airline:
        sql = '''SELECT * FROM flight_data
                     WHERE airline=?
                     AND origin=?
                     AND day>?
                     AND day<?
                     AND month=?'''
        params = (airline, origin, (day - window), (day + window), month)
    else:
        sql = '''SELECT * FROM flight_data
                     WHERE origin=?
                     AND day>?
                     AND day<?
                     AND month=?'''
        params = (origin, (day - window), (day + window), month)
    return params, sql


def select_query_complex(airline, end_day, end_month, origin, start_day, start_month):
    if airline:
        sql = '''SELECT * FROM flight_data
                     WHERE airline=?
                     AND origin=?
                     AND day>?
                     AND month=?
                     UNION
                     SELECT * FROM flight_data
                     WHERE airline=?
                     AND origin=?
                     AND day<?
                     AND month=?'''
        params = (airline, origin, start_day, start_month, airline, origin, end_day, end_month)
    else:
        sql = '''SELECT * FROM flight_data
                     WHERE origin=?
                     AND day>?
                     AND month=?
                     UNION
                     SELECT * FROM flight_data
                     WHERE origin=?
                     AND day<?
                     AND month=?'''
        params = (origin, start_day, start_month, origin, end_day, end_month)
    return params, sql


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
        return 'NOT FOUND'


@app.route('/newUser', methods=['POST', 'GET'])
def create_user():
    cur = conn.cursor()
    if request.method == 'POST':
        user_name = request.form['username']
        pw = request.form['password']

        cur.execute('''INSERT INTO user (username, password)
                 VALUES (?, ?)''', (user_name, pw))
        conn.commit()
        cur.execute('''SELECT user_id FROM user WHERE username=? AND password=?;''', (user_name, pw))
        rows = cur.fetchone()
        print(rows)
        return redirect(url_for('add_flight', userId=rows[0]))
    else:
        return render_template('create_user.html')


@app.route('/<userId>/addFlight', methods=['POST', 'GET'])
def add_flight(userId):
    cur = conn.cursor()
    if request.method == 'POST':

        sql = '''INSERT INTO flight_data (airline, origin, destination, year, month, day, sched_hour, sched_min, act_hour, act_min, delayed, user_id)
                 VALUES (?,?,?,?,?,?,?,?,?,?,?,?)'''
        params = generate_params() + (userId,)
        cur.execute(sql, params)
        conn.commit()
        print("HERE")
        return redirect(url_for('add_flight', userId=userId))

    cur.execute('''SELECT * FROM flight_data WHERE user_id=?;''', (userId,))
    rows = cur.fetchall()
    return render_template('add_flight.html', rows=rows, userId=userId)


@app.route('/<userId>/<flightId>/deleteFlight', methods=['POST', 'GET'])
def delete_flight(userId, flightId):
    cur = conn.cursor()
    sql = '''DELETE FROM flight_data WHERE user_id=? AND flight_id=?;'''
    params = (userId, flightId)
    cur.execute(sql, params)
    conn.commit()
    return redirect(url_for('add_flight', userId=userId))


@app.route('/<userId>/<flightId>/edit', methods=['POST', 'GET'])
def edit_flight(userId, flightId):
    cur = conn.cursor()
    if request.method == 'POST':
        sql = '''UPDATE flight_data
                 SET airline=?, origin=?, destination=?, year=?, month=?, day=?, sched_hour=?, sched_min=?, act_hour=?, act_min=?, delayed=?
                 WHERE flight_id=?;'''
        params = generate_params() + (flightId,)
        cur.execute(sql, params)
        conn.commit()
        return redirect(url_for('add_flight', userId=userId))
    else:
        sql_select = '''SELECT * FROM flight_data WHERE flight_id=?;'''
        params_select = (flightId,)
        cur.execute(sql_select, params_select)
        flight = cur.fetchone()
        return render_template('edit_flight.html', userId=userId, flightId=flightId, flight=flight)


@app.route('/search', methods=['POST', 'GET'])
def search_flight():
    results = None
    indicator = 0
    data = {}
    if request.method == 'POST':
        cur = conn.cursor()
        airline = request.form['airline']
        origin_airport = request.form['origin_airport']
        dept_date = request.form['dept_date']

        data = {'airline': airline, 'origin': origin_airport, 'date': dept_date}

        year = int(dept_date[0:4])
        month = int(dept_date[5:7])
        day = int(dept_date[8:10])
        sched_hour = int(dept_date[11:13])
        sched_minute = int(dept_date[14:])

        results = get_flights_in_window(4, day, month, year, origin_airport, airline)

        value = [0] * 24
        counts = [0] * 24

        for res in results:
            if res[9] != 'NA' and type(res[10]) is int:
                delay = calc_delay(res[4], res[5], res[6], res[7], res[8], res[9], res[10])
                hour = res[7]
                value[hour] += delay
                counts[hour] += 1

        for i in range(24):
            if counts[i] > 0:
                value[i] /= counts[i]

        indicator = value[sched_hour]

    return render_template('search_flight.html', results=results, p_val=indicator, data=data)


@app.route('/getFig/<origin>/<airline>/<date>')
def get_fig(origin, airline, date):
    cur = conn.cursor()

    year = int(date[0:4])
    month = int(date[5:7])
    day = int(date[8:10])
    sched_hour = int(date[11:13])
    sched_minute = int(date[14:])

    results = get_flights_in_window(4, day, month, year, origin, airline)

    value = [0] * 24
    counts = [0] * 24

    for res in results:
        if res[9] != 'NA' and type(res[10]) is int:
            delay = calc_delay(res[4], res[5], res[6], res[7], res[8], res[9], res[10])
            hour = res[7]
            value[hour] += delay
            counts[hour] += 1

    for i in range(24):
        if counts[i] > 0:
            value[i] /= counts[i]

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

    results = get_flights_in_window(4, day, month, year, origin, airline=None)
    value = [0] * 24
    counts = [0] * 24
    airline = {}

    fig, ax = plt.subplots()

    for res in results:
        if res[9] != 'NA' and type(res[10]) is int and type(res[4]) is int and type(res[5]) is int and type(res[6]) \
                is int and type(res[7]) is int and type(res[8]) is int:
            delay = calc_delay(res[4], res[5], res[6], res[7], res[8], res[9], res[10])
            hour = res[7]
            value[hour] += delay
            counts[hour] += 1
            if res[1] not in airline:
                airline[res[1]] = [0, 0]
            airline[res[1]][0] += delay
            airline[res[1]][1] += 1

    for carrier in airline:
        airline[carrier] = airline[carrier][0]/airline[carrier][1]
    print(airline)

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

    window = 4
    results = get_flights_in_window(window, day, month, year, origin, airline)
    n = (2 * window) - 1
    airline_dict = {}

    fig, ax = plt.subplots()

    for res in results:
        if res[9] != 'NA' and type(res[10]) is int:
            delay = calc_delay(res[4], res[5], res[6], res[7], res[8], res[9], res[10])
            day = str(res[6])
            if day not in airline_dict:
                airline_dict[day] = [0, 0]
            airline_dict[day][0] += delay
            airline_dict[day][1] += 1

    for carrier in airline_dict:
        airline_dict[carrier] = airline_dict[carrier][0]/airline_dict[carrier][1]

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
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    app.run()
