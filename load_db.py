import csv
import datetime
import sqlite3
from sqlite3 import Error
import os


conn = None


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(e)
        return None


def create_flight_table(conn):
    cur = conn.cursor()
    sql = '''
          DROP TRIGGER IF EXISTS validateDate
          '''
    cur.execute(sql)
    sql = '''
          CREATE TRIGGER IF NOT EXISTS validateDate
          BEFORE INSERT ON flights
          WHEN NEW.year < 1903 OR NEW.month <= 0 OR NEW.day <= 0
          BEGIN
          SELECT RAISE(ABORT, 'Year, month, and day must be greater than 0.');
          END;
          '''
    cur.execute(sql)
    sql = '''
          CREATE TABLE IF NOT EXISTS flights (
            flight_id   INTEGER        PRIMARY KEY AUTOINCREMENT,
            airline     STRING (2, 20) NOT NULL,
            origin      STRING (2, 20) NOT NULL,
            destination STRING (2, 20) NOT NULL,
            year        INTEGER        NOT NULL,
            month       INTEGER        NOT NULL,
            day         INTEGER        NOT NULL,
            sched_hour  INTEGER        NOT NULL,
            sched_min   INTEGER        NOT NULL,
            delay       INTEGER        NOT NULL,
            delayed     BOOLEAN        NOT NULL,
            user_id     INTEGER
        );
        '''
    cur.execute(sql)
    conn.commit()


def create_user_table(conn):
    sql = '''
        CREATE TABLE IF NOT EXISTS user (
        user_id  INTEGER        PRIMARY KEY AUTOINCREMENT,
        username STRING (3, 20) NOT NULL,
        password STRING (3, 20) NOT NULL
        );
    '''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def create_wait_time_table(conn):
    sql = '''
    CREATE TABLE IF NOT EXISTS wait_time (
        id       INTEGER        NOT NULL
                                PRIMARY KEY AUTOINCREMENT,
        airport  STRING (2, 20) NOT NULL,
        year     INTEGER        NOT NULL,
        month    INTEGER        NOT NULL,
        day      INTEGER        NOT NULL,
        hour     INTEGER        NOT NULL,
        avg_wait INTEGER        NOT NULL,
        max_wait INTEGER        NOT NULL
    );
    '''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()


def create_wait_view(conn):
    cur = conn.cursor()
    sql = '''
        DROP VIEW IF EXISTS avg_waits
    '''
    cur.execute(sql)
    conn.commit()
    sql = '''
        CREATE VIEW IF NOT EXISTS avg_waits AS
        SELECT airport, month, day, hour, AVG(avg_wait) AS avg_wait, AVG(max_wait) as avg_max_wait
        FROM wait_time
        GROUP BY airport, month, day, hour;
        '''
    cur.execute(sql)
    conn.commit()


def create_test_environment(db_path, csv_path, skip_num):
    conn = create_connection(db_path)
    create_flight_table(conn)
    create_user_table(conn)
    create_wait_time_table(conn)
    db_import(csv_path, conn, skip_num)
    import_files(conn, test=True)
    create_wait_view(conn)


def create_normal_environment(db_path, csv_path):
    conn = create_connection(db_path)
    create_flight_table(conn)
    create_user_table(conn)
    create_wait_time_table(conn)
    db_import(csv_path, conn, 1)
    import_files(conn)
    create_wait_view(conn)


def toTime(str):
    if len(str) == 3:
        str = '0' + str
    return str


def stringToDate(year, month, day):
    return datetime.date(year, month, day)


def toDateTime(str):
    return datetime.datetime.strptime(str, "%Y%m%d%H%M")


def db_import(file_path, conn, test_num=1):
    cur = conn.cursor()
    with open(file_path, 'r+') as csv_file:
        spamreader = csv.reader(csv_file)
        next(spamreader)
        count = 0
        count_counter = 0
        for line in spamreader:
            count_counter += 1
            if count_counter % test_num == 0 and '' not in line[:18]:

                airline = line[8]
                origin = line[16]
                destination = line[17]
                year = line[0]
                try:
                    year = int(year)
                except ValueError:
                    continue
                month = line[1]
                if int(month) < 10:
                    month = '0' + month
                day = line[2]
                if int(day) < 10:
                    day = '0' + day
                sched_time = toTime(line[5])
                try:
                    int(sched_time)
                except ValueError:
                    continue
                hour = sched_time[0:2]
                try:
                    hour = int(hour)
                except ValueError:
                    continue
                minute = sched_time[2:]
                try:
                    minute = int(minute)
                except ValueError:
                    continue
                delay = line[15]
                try:
                    delay = int(delay)
                except ValueError:
                    continue
                if delay > 15:
                    delayed = 1
                else:
                    delayed = 0

                sql = '''INSERT INTO flights (airline, origin, destination, year, month, day, sched_hour, sched_min, delay, delayed, user_id)
                     VALUES (?,?,?,?,?,?,?,?,?,?,?)'''
                params = (airline, origin, destination, year, int(month), int(day), hour, minute, delay, delayed, None)
                cur.execute(sql, params)
                count += 1
                if count % 100 == 0:
                    print(count)
                    conn.commit()


def import_files(conn, test=False):
    file_names = os.listdir('/Users/Max/Downloads/CS424-Airport-Wait-Time-master/HTML')
    cur = conn.cursor()
    count = 0
    seen_airports = {}
    for file_path in file_names:
        code = file_path.split('_')[0]
        file_path = '/Users/Max/Downloads/CS424-Airport-Wait-Time-master/HTML/' + file_path
        if not test or code not in seen_airports:
            with open(file_path, 'r+') as csv_file:
                fildes = csv.reader(csv_file)
                next(fildes)
                for line in fildes:
                    airport = line[0]
                    date = line[2]
                    if '/' in date:
                        month = int(date.split('/')[0])
                        day = int(date.split('/')[1])
                        year = int(date.split('/')[2])
                    else:
                        month = int(date.split('-')[0])
                        day = int(date.split('-')[1])
                        year = int(date.split('-')[2])
                    hour = int(line[3].split(' ')[0]) / 100
                    avg_wait = int(line[4])
                    max_wait = int(line[5])
                    sql = '''INSERT INTO wait_time (airport, year, month, day, hour, avg_wait, max_wait)
                         VALUES (?,?,?,?,?,?,?)'''
                    params = (airport, year, month, day, hour, avg_wait, max_wait)
                    cur.execute(sql, params)
                    count += 1
                    if count % 100 == 0:
                        print(count)
                        conn.commit()
            seen_airports[code] = True


if __name__ == '__main__':
    #create_test_environment('test.db', '/Users/Max/Downloads/2007.csv', 5)
    #create_normal_environment('flights.db', '/Users/Max/Downloads/2007.csv')
    conn = create_connection('test.db')
    create_flight_table(conn)