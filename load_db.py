import csv
import datetime
import sqlite3
from sqlite3 import Error


conn = None


def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
    except Error as e:
        print(e)
        return None


def toTime(str):
    if len(str) == 3:
        str = '0' + str
    return str
    #timeRep = str[:2] + ':' + str[2:]
    #time = datetime.datetime.strptime(timeRep, '%H:%M').hour
    #return timeRep


def stringToDate(year, month, day):
    return datetime.date(year, month, day)


def toDateTime(str):
    return datetime.datetime.strptime(str, "%Y%m%d%H%M")


def db_import(file_path):
    conn = create_connection('/Users/Max/PycharmProjects/CS411/flights.db')
    cur = conn.cursor()
    with open(file_path, 'r+') as csv_file:
        #csv_file.seek(1000,0)
        spamreader = csv.reader(csv_file)
        next(spamreader)
        count = 0
        count_counter = 0
        for line in spamreader:
            count_counter += 1
            if count_counter % 10 == 0:
                # airline = line['UniqueCarrier']
                # origin = line['Orgin']
                # destination = line['Dest']
                # year = line['Year']
                # month = line['Month']
                # day = line['DayofMonth']
                # sched_time = line['CRSDepTime']
                # dep_time = line['DepTime']
                # delay = line['DepDelay']

                airline = line[8]
                origin = line[16]
                destination = line[17]
                year = line[0]
                month = line[1]
                if int(month) < 10:
                    month = '0' + month
                day = line[2]
                if int(day) < 10:
                    day = '0' + day
                sched_time = toTime(line[5])
                dep_time = toTime(line[4])
                delay = line[15]
                if delay > 0:
                    delayed = 1
                else:
                    delayed = 0

                if dep_time != 'NA':
                    sql = '''INSERT INTO flight_data (airline, origin, destination, year, month, day, sched_hour, sched_min, act_hour, act_min, delayed, user_id)
                         VALUES (?,?,?,?,?,?,?,?,?,?,?,?)'''
                    params = (airline, origin, destination, year, month, day, sched_time[0:2], sched_time[2:], dep_time[0:2], dep_time[2:], delayed, None)
                    cur.execute(sql, params)
                    count += 1
                    if count % 100 == 0:
                        print(count)
                        conn.commit()

if __name__ == '__main__':
    #db_import('/Users/Max/PycharmProjects/CS411/sample.csv')
    db_import('/Users/Max/Downloads/2007.csv')

