#!/usr/bin/env python
# -*- coding: utf-8 -*-

import denki_db

import logging
logging.basicConfig(
   level=logging.DEBUG,
   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
   filename="show_denkidb.log"
)
logger = logging.getLogger("DenkiLog")
logger.debug("Start DenkiDB System\n")

print('open')
denki_db.open_db()
print("")

print('tables')
rows = denki_db.print_all_tables()
for row in rows:
  print(row)
print("")

print('InstantaneousPower colums')
rows = denki_db.print_colums('integral_power')
for row in rows:
  print(row)
print("")

print('instantaneous_power colums')
rows = denki_db.print_colums('instantaneous_power')
for row in rows:
  print(row)
print("")

print('InstantaneousPower')
rows = denki_db.print_InstantaneousPower()
for row in rows:
  print(row)
print("")

print('IntegralPower')
rows = denki_db.print_IntegralPower()
for row in rows:
  print(row)
print("")

print('close')
denki_db.close_db()
print("")
