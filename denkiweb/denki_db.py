#!/usr/bin/env python
# -*- coding: utf-8 -*-

import denki_idpass # ソース公開用にIDとPasswordを別ファイルに

from datetime import datetime, date, timedelta

import psycopg2
conn = None

import logging
logger = logging.getLogger("DenkiWebLog").getChild("postgres")

# denki_DBのオープン
def open_db():
    global conn
    try:
        # connect to the PostgreSQL server
        #conn = psycopg2.connect("host=AAA.BBB.CCC.DDD port=5432 dbname=XXXXX user=YYYYY password=ZZZZZ")
        conn  = psycopg2.connect(denki_idpass.progres_idpwd)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't open Database\n")
        exit()
    finally:
        logger.debug("Success: Open Database\n")

# denki_DBのクローズ
def close_db():
    global conn
    try:
        # close the PostgreSQL server
        if conn!=None:
           conn.close()
           conn=None
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't close Database\n")
        exit()
    finally:
        logger.debug("Success: close Database\n")

# denki_DBのテーブル作成
def create_table():
    global conn
    cmd = ("CREATE TABLE instantaneous_power (id serial PRIMARY KEY,"
           "datetime timestamp NOT NULL,"
           "power integer);")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't create table(instantaneous_power)\n")
        exit()
    finally:
        logger.debug("Success: Create Table(instantaneous_power)\n")

    cmd = ("CREATE TABLE integral_power (id serial PRIMARY KEY,"
           "datetime timestamp NOT NULL,"
           "power integer);")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't create table(integral_power)\n")
        exit()
    finally:
        logger.debug("Success: Create Table(integral_power)\n")

# 瞬時電力の記録
def insert_InstantaneousPower(datetime, power):
    global conn
    cmd = ("INSERT INTO instantaneous_power (datetime, power) "
           "VALUES ('{dt}','{pwr}');".format(dt=datetime,pwr=power))
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't insert InstantaneousPower\n")
        exit()
    finally:
        logger.debug("Success: insert InstantaneousPower\n")

# 定時積算電力の記録
def insert_IntegralPower(datetime, power):
    global conn
    cmd = ("INSERT INTO integral_power (datetime, power) "
           "VALUES ('{dt}','{pwr}');".format(dt=datetime,pwr=power))
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't insert IntegralPower\n")
        exit()
    finally:
        logger.debug("Success: insert IntegralPower\n")


# テーブルの一覧を参照
def print_all_tables():
    global conn
    cmd = ("select relname as TABLE_NAME from pg_stat_user_tables")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        rows = cur.fetchall()
        conn.commit()
        # print(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't get all_tables\n")
        exit()
    finally:
        logger.debug("Success: print_all_tables\n")
    return rows

# カラム一覧を参照
def print_colums(table_name):
    global conn
    cmd = ("select * from information_schema.columns where " + \
           "table_catalog='denkidb' and " + \
           "table_name='" + table_name + "' order by ordinal_position;")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        rows = cur.fetchall()
        conn.commit()
        # print(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't get all_tables\n")
        exit()
    finally:
        logger.debug("Success: print_all_tables\n")
    return rows

# 瞬時電力の値を参照
def print_InstantaneousPower():
    global conn
    cmd = ("SELECT * from instantaneous_power;")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        rows = cur.fetchall()
        conn.commit()
        # print(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't get Instantaneous Power\n")
        exit()
    finally:
        logger.debug("Success: get InstantaneousPower all\n") 
    return rows

# 今の瞬時電力の値を参照
def get_InstantaneousPower_now():
    global conn
    cmd = ("SELECT * from instantaneous_power where date=(select max(date) from instantaneous_power);")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        rows = cur.fetchall()
        conn.commit()
        # print(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't get Instantaneous Power now\n")
        exit()
    finally:
        logger.debug("Success: get Instantaneous Power now\n") 
    return rows

# 定時積算電力の値を参照
def print_IntegralPower():
    global conn
    cmd = ("SELECT * from integral_power;")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        rows = cur.fetchall()
        conn.commit()
        # print(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't get Integral Power\n")
        exit()
    finally:
        logger.debug("Success: get Integral Power\n") 
    return rows

# 今の瞬時電力の値を参照
def get_InstantaneousPower_now():
    global conn
    cmd = ("SELECT * from instantaneous_power where datetime=(select max(datetime) from instantaneous_power);")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        row = cur.fetchone()
        conn.commit()
        # print(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't insert InstantaneousPower now\n")
        exit()
    finally:
        logger.debug("Success: InstantaneousPower now\n") 
    return row

# 指定時間内の瞬時電力の値を参照
def get_InstantaneousPower_period(starttime, endtime):
    global conn
    cmd = ("SELECT * from instantaneous_power where datetime between '"+starttime+"' and '"+endtime+"' order by datetime;")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        rows = cur.fetchall()
        conn.commit()
        # print(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't insert InstantaneousPower now\n")
        exit()
    finally:
        logger.debug("Success: InstantaneousPower now\n") 
    return rows


# 指定時間内の積算電力の値を参照
def get_IntegralPower_period(starttime, endtime):
    global conn
    cmd = ("SELECT * from integral_power where datetime between '"+starttime+"' and '"+endtime+"' order by datetime;")
    try:
        cur = conn.cursor()
        cur.execute(cmd)
        rows = cur.fetchall()
        conn.commit()
        # print(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't insert integral_power\n")
        exit()
    finally:
        logger.debug("Success: integral_power\n") 
    return rows

# 指定日の電気使用量を算出
def get_SpecefiedDate_IntegralPower(date):
    global conn
  
    try:
        cur = conn.cursor()
        # 指定日の積算電力の値
        starttime = date + u" 00:00:05"
        dt = datetime.strptime(date, '%Y-%m-%d')
        endtime = (dt+timedelta(days=1)).strftime("%Y-%m-%d") + u" 00:00:05"
        cmd = ("SELECT * from integral_power where datetime between '"+starttime+"' and '"+endtime+"' order by datetime DESC LIMIT 1;")
        cur.execute(cmd)
        row1 = cur.fetchone()
        # 指定日前日の積算電力の値
        starttime = (dt-timedelta(days=1)).strftime("%Y-%m-%d") + u" 00:00:05"
        dt = datetime.strptime(date, '%Y-%m-%d')
        endtime = date + u" 00:00:05"
        cmd = ("SELECT * from integral_power where datetime between '"+starttime+"' and '"+endtime+"' order by datetime DESC LIMIT 1;")
        cur.execute(cmd)
        row2 = cur.fetchone()
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't insert integral_power\n")
        exit()
    finally:
        logger.debug("Success: integral_power\n") 
    if (row1 is None) or (row2 is None):
        return [ 0, dt, 0]
    else:
        return [row2[0], dt, row1[2]-row2[2]]

# 最近一週間分の使用電力量の値を算出
def get_NearWeek_IntegralPower():
    #global conn
    try:
        rows = []
        list1 = [6,5,4,3,2,1,0]
        for d in list1:
          date = (datetime.today()-timedelta(days=d)).strftime("%Y-%m-%d")
          row = get_SpecefiedDate_IntegralPower(date)
          rows.append(row)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't insert integral_power\n")
        exit()
    finally:
        logger.debug("Success: integral_power\n") 
    return rows

# 指定日からnum日分の毎日の使用電力量の値を算出
def get_Daily_IntegralPower_fromSpecifiedDate(date, numday):
    #global conn
    try:
        rows = []
        dt = datetime.strptime(date, '%Y-%m-%d')
        list1 = range(0, numday)
        for d in list1:
          date = (dt+timedelta(days=d)).strftime("%Y-%m-%d")
          row = get_SpecefiedDate_IntegralPower(date)
          rows.append(row)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        logger.error("Error: Can't insert integral_power\n")
        exit()
    finally:
        logger.debug("Success: integral_power\n") 
    return rows




