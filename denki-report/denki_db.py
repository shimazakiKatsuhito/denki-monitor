#!/usr/bin/env python
# -*- coding: utf-8 -*-

import psycopg2
conn = None

import logging
logger = logging.getLogger("DenkiLog").getChild("postgres")

# denki_DBのオープン
def open_db():
    global conn
    try:
        # connect to the PostgreSQL server
        conn = psycopg2.connect("host=192.168.8.80 port=5432 dbname=denkidb user=denkiusr password=passwd00")
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
        logger.debug("Success: InstantaneousPower\n")

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
        logger.debug("Success: IntegralPower\n")


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

