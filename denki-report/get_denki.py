#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
sys.path.append('/home/katsu/.local/lib/python2.7/site-packages')
import codecs
sys.stdout = codecs.EncodedFile(sys.stdout, 'utf_8')
import serial
import time
from datetime import datetime
import echonet_lite
import denki_idpass # ソース公開用にIDとPasswordを別ファイルに
import denki_db

import logging
import denki_log
logging.basicConfig(
   level=denki_log.log_level,
   format=denki_log.log_format,
   filename=denki_log.log_filename
)
logger = logging.getLogger("DenkiLog")
logger.debug("Start DenkiDB System\n")

# denkiDB(postgreSQL)のオープン
denki_db.open_db()

# Bルート認証ID（Bルート申請すると電力会社から郵送で送られてくる）
#rbid = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
rbid  = denki_idpass.rbid
# Bルート認証パスワード（Bルート申請すると電力会社から郵送で送られてくる）
#rbpwd = "YYYYYYYYYYYY"
rbpwd = denki_idpass.rbpwd

# シリアルポートデバイス名
#serialPortDev = 'COM3'  # Windows の場合
serialPortDev = '/dev/ttyUSB0'  # Linux(ラズパイなど）の場合
#serialPortDev = '/dev/cu.usbserial-A103BTPR'    # Mac の場合

# シリアルポート初期化
ser = serial.Serial(serialPortDev, 115200)

# IDおよびパスワードの設定
echonet_lite.set_id_and_password(ser, rbid, rbpwd)

# 電力メーターをスキャンし、IPアドレス取得
logger.debug("Scan ipv6_Address\n")
ipv6Addr = echonet_lite.scan_and_getIpAddr(ser)


# 接続開始
logger.debug("Start connect.\n")
bConnected = echonet_lite.open_connect(ser, ipv6Addr)
if not bConnected:
  logger.error("Start connect.\n")
else:
  logger.debug("Succces connected.\n")

# これ以降、シリアル通信のタイムアウトを設定
ser.timeout = 2

# スマートメーターがインスタンスリスト通知を投げてくる
# (ECHONET-Lite_Ver.1.12_02.pdf p.4-16)
logger.debug(ser.readline()) #無視


# 積算電力量単位の取得
unitIntegralPower = echonet_lite.getUnitIntegralPower(ser, ipv6Addr)

base_time = time.time()
next_time = 0

interval = 60
flagIntegral = 1

while True:
    dtnow = datetime.now()
    minute = int(dtnow.strftime('%M'))
    #print(dtnow.strftime('%Y/%m/%d %H:%M:%S'))

    # 1分間に1回
    # 瞬時電力の取得
    while True:
        power = echonet_lite.getInstantaneousPower(ser, ipv6Addr)
        if(power<0):
            # 通信に失敗したら、接続からやり直し
            # 電力メーターをスキャンし、IPアドレス取得
            ipv6Addr = echonet_lite.scan_and_getIpAddr(ser)
            # 接続開始
            bConnected = echonet_lite.open_connect(ser, ipv6Addr)
            # スマートメーターがインスタンスリスト通知を投げてくる
            # (ECHONET-Lite_Ver.1.12_02.pdf p.4-16)
            logger.debug(ser.readline()) #無視
        else:
            # 使用電力量をDBに登録
            denki_db.insert_InstantaneousPower(dtnow, power)
            break

    # 30分間に1回
    # 定時積算電力量計測値の取得
    while True:
        if(flagIntegral == 0 and 1 < minute and minute < 25):
            integralPower = echonet_lite.getIntegralPower(ser, ipv6Addr, unitIntegralPower)
            if(integralPower<0):
                # 通信に失敗したら、接続からやり直し
                # 電力メーターをスキャンし、IPアドレス取得
                ipv6Addr = echonet_lite.scan_and_getIpAddr(ser)
                # 接続開始
                bConnected = echonet_lite.open_connect(ser, ipv6Addr)
                # スマートメーターがインスタンスリスト通知を投げてくる
                # (ECHONET-Lite_Ver.1.12_02.pdf p.4-16)
                logger.debug(ser.readline()) #無視
            else:
                # 使用電力量をDBに登録
                integralTime = datetime.strptime('{}/{}/{} {}:{}:{}'.format(integralPower[0],integralPower[1], integralPower[2], integralPower[3], integralPower[4], integralPower[5]), '%Y/%m/%d %H:%M:%S')
                denki_db.insert_IntegralPower(integralTime, integralPower[6])
                flagIntegral = 1
                break
        elif(flagIntegral == 1 and 31 < minute and minute < 55):
            integralPower = echonet_lite.getIntegralPower(ser, ipv6Addr, unitIntegralPower)
            if(integralPower<0):
                # 通信に失敗したら、接続からやり直し
                # 電力メーターをスキャンし、IPアドレス取得
                ipv6Addr = echonet_lite.scan_and_getIpAddr(ser)
                # 接続開始
                bConnected = echonet_lite.open_connect(ser, ipv6Addr)
                # スマートメーターがインスタンスリスト通知を投げてくる
                # (ECHONET-Lite_Ver.1.12_02.pdf p.4-16)
                logger.debug(ser.readline()) #無視
            else:
                # 使用電力量をDBに登録
                integralTime = datetime.strptime('{}/{}/{} {}:{}:{}'.format(integralPower[0],integralPower[1], integralPower[2], integralPower[3], integralPower[4], integralPower[5]), '%Y/%m/%d %H:%M:%S')
                denki_db.insert_IntegralPower(integralTime, integralPower[6])
                flagIntegral = 0
                break
        else:
            break
        
    next_time = ((base_time - time.time()) % interval) or interval
    time.sleep(next_time)


# 無限ループだからここには来ないけどな
ser.close()



