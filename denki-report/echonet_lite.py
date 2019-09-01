#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import serial
import time

import logging
logger = logging.getLogger("DenkiLog").getChild("echonet")

# IDとパスワード設定
def set_id_and_password(ser, rbid, rbpwd):
    # とりあえずバージョンを取得してみる（やらなくてもおｋ）
    ser.write("SKVER\r\n")
    logger.debug(ser.readline()) # エコーバック
    logger.debug(ser.readline()) # バージョン

    # Bルート認証パスワード設定
    ser.write("SKSETPWD C " + rbpwd + "\r\n")
    logger.debug(ser.readline()) # エコーバック
    logger.debug(ser.readline()) # OKが来るはず（チェック無し）

    # Bルート認証ID設定
    ser.write("SKSETRBID " + rbid + "\r\n")
    logger.debug(ser.readline()) # エコーバック
    logger.debug(ser.readline()) # OKが来るはず（チェック無し）

# 電力メーターをスキャンし、IPアドレス取得
def scan_and_getIpAddr(ser):
    scanDuration = 6; # スキャン試行回数の初期値。（ダメなら増やして再試行）
    scanDuration_max = 10  # スキャン試行回数の最大値。# 引数としては14まで指定できるが、7で失敗したらそれ以上は無駄っぽい
    scanRes = {} # スキャン結果の入れ物
    
    # スキャンのリトライループ（何か見つかるまで）
    while not scanRes.has_key("Channel") :
        # アクティブスキャン（IE あり）を行う
        # 時間かかります。10秒ぐらい？
        ser.write("SKSCAN 2 FFFFFFFF " + str(scanDuration) + "\r\n")
         
        # スキャン1回について、スキャン終了までのループ
        scanEnd = False
        while not scanEnd :
            line = ser.readline()
            logger.debug(line)

            if line.startswith("EVENT 22") :
                # スキャン終わったよ（見つかったかどうかは関係なく）
                scanEnd = True
            elif line.startswith("  ") :
                # スキャンして見つかったらスペース2個あけてデータがやってくる
                # 例
                #  Channel:39
                #  Channel Page:09
                #  Pan ID:FFFF
                #  Addr:FFFFFFFFFFFFFFFF
                #  LQI:A7
                #  PairID:FFFFFFFF
                cols = line.strip().split(':')
                scanRes[cols[0]] = cols[1]
                
        scanDuration+=1    
        if scanDuration_max < scanDuration and not scanRes.has_key("Channel"):
            logger.error("スキャンリトライオーバー")
            sys.exit()  #### 終了 ####
     
    # スキャン結果からChannelを設定。
    ser.write("SKSREG S2 " + scanRes["Channel"] + "\r\n")
    logger.debug(ser.readline()) # エコーバック
    logger.debug(ser.readline()) # OKが来るはず（チェック無し）

    # スキャン結果からPan IDを設定
    ser.write("SKSREG S3 " + scanRes["Pan ID"] + "\r\n")
    logger.debug(ser.readline()) # エコーバック
    logger.debug(ser.readline()) # OKが来るはず（チェック無し）

    # MACアドレス(64bit)をIPV6リンクローカルアドレスに変換。
    # (BP35A1の機能を使って変換しているけど、単に文字列変換すればいいのではという話も？？)
    ser.write("SKLL64 " + scanRes["Addr"] + "\r\n")
    logger.debug(ser.readline()) # エコーバック
    ipv6Addr = ser.readline().strip()
    logger.debug("ipv6Addr="+str(ipv6Addr))
    
    return ipv6Addr

# 接続開始
def open_connect(ser, ipv6Addr):
    # PANA 接続シーケンスを開始します。
    ser.write("SKJOIN " + ipv6Addr + "\r\n");
    logger.debug(ser.readline()) # エコーバック
    logger.debug(ser.readline()) # OKが来るはず（チェック無し）

    bConnected = False
    # PANA 接続完了待ち（10行ぐらいなんか返してくる）
    while not bConnected :
        line = ser.readline()
        print(line, end="")
        if line.startswith("EVENT 24") :
            logger.error("PANA 接続失敗")
            sys.exit()  #### 終了 ####
        elif line.startswith("EVENT 25") :
            # 接続完了！
            bConnected = True
            return  bConnected

# ECHONET Lite フレーム作成
def make_echonetlite_command_frame(epc):
    # 　参考資料
    # 　・ECHONET-Lite_Ver.1.12_02.pdf (以下 EL)
    # 　・Appendix_H.pdf (以下 AppH)
    echonetLiteFrame = ""
    echonetLiteFrame += "\x10\x81"      # EHD (参考:EL p.3-2)
    echonetLiteFrame += "\x00\x01"      # TID (参考:EL p.3-3)
    # ここから EDATA
    echonetLiteFrame += "\x05\xFF\x01"  # SEOJ (参考:EL p.3-3 AppH p.3-408～)
    echonetLiteFrame += "\x02\x88\x01"  # DEOJ (参考:EL p.3-3 AppH p.3-274～)
    echonetLiteFrame += "\x62"          # ESV(62:プロパティ値読み出し要求) (参考:EL p.3-5)
    echonetLiteFrame += "\x01"          # OPC(1個)(参考:EL p.3-7)
    echonetLiteFrame += epc             # EPC(参考:EL p.3-7 AppH p.3-275)
    echonetLiteFrame += "\x00"          # PDC(参考:EL p.3-9)
    return echonetLiteFrame

# ECHONET Lite コマンド送信
def send_echonetlite_command(ser, ipv6Addr, cmd):
    command = "SKSENDTO 1 {0} 0E1A 1 {1:04X} {2}".format(ipv6Addr, len(cmd), cmd)
    ser.write(command)

    logger.debug(ser.readline()) # エコーバック
    logger.debug(ser.readline()) # EVENT 21 が来るはず（チェック無し）
    logger.debug(ser.readline()) # OKが来るはず（チェック無し）
    line = ser.readline()         # ERXUDPが来るはず
    logger.debug(line)
    return line

# ECHONET Lite 応答チェック
def check_echonetlite_receive(line, epc):
    # 受信データはたまに違うデータが来たり、
    # 取りこぼしたりして変なデータを拾うことがあるので
    # チェックを厳しめにしてます。
    if line.startswith("ERXUDP") :
        cols = line.strip().split(' ')
        res = cols[8]   # UDP受信データ部分
        #tid = res[4:4+4];
        seoj = res[8:8+6]
        #deoj = res[14,14+6]
        ESV = res[20:20+2]
        #OPC = res[22,22+2]
        if seoj == "028801" and ESV == "72" :
            # スマートメーター(028801)から来た応答(72)なら受信成功
            EPC = res[24:24+2]
            if EPC == epc :
                return True

# 積算電力量単位の取得
def getUnitIntegralPower(ser, ipv6Addr):
    # 積算電力量単位の取得のコマンドフレーム作成
    cmd = make_echonetlite_command_frame("\xE1") # EPC(参考:EL p.3-7 AppH p.3-275) 積算電力量単位
    
    for i in range(5): # リトライ5回
        # コマンド送信＆結果受信
        line = send_echonetlite_command(ser, ipv6Addr, cmd)

        unitIntegralPower = 1.0
        # 受信結果の確認と変換
        if check_echonetlite_receive(line, "E1") :
            # 内容が積算電力量単位(E1)だったら
            hexUnit = line[-2:]    # 最後の4バイト（16進数で8文字）が瞬時電力計測値
            if hexUnit == "00":
                unitIntegralPower = 1.0
            elif hexUnit == "01":
                unitIntegralPower = 0.1
            elif hexUnit == "02":
                unitIntegralPower = 0.01
            elif hexUnit == "03":
                unitIntegralPower = 0.001
            elif hexUnit == "04":
                unitIntegralPower = 0.0001
            elif hexUnit == "0A":
                unitIntegralPower = 10.0
            elif hexUnit == "0B":
                unitIntegralPower = 100.0
            elif hexUnit == "0C":
                unitIntegralPower = 1000.0
            elif hexUnit == "0D":
                unitIntegralPower = 10000.0
            logger.debug("積算電力量単位:{0}[kW]".format(unitIntegralPower))
            return unitIntegralPower
        else:
            time.sleep(1)
    logger.error("積算電力量単位の取得に失敗")
    return -1 # リトライしてだめならエラー応答(-1)


# 瞬時電力の取得
def getInstantaneousPower(ser, ipv6Addr):
    # 瞬時電力の取得のコマンドフレーム作成
    cmd = make_echonetlite_command_frame("\xE7") # EPC(参考:EL p.3-7 AppH p.3-275) 瞬時電力
    
    for i in range(5): # リトライ5回
        # コマンド送信＆結果受信
        line = send_echonetlite_command(ser, ipv6Addr, cmd)

        # 受信結果の確認と変換
        if check_echonetlite_receive(line, "E7") :
            # 内容が瞬時電力計測値(E7)だったら
            hexPower = line[-8:]    # 最後の4バイト（16進数で8文字）が瞬時電力計測値
            intPower = int(hexPower, 16)
            logger.debug("瞬時電力計測値:{0}[W]".format(intPower))
            return intPower
        else:
            time.sleep(1)
    logger.error("瞬時電力の取得に失敗")
    return -1 # リトライしてだめならエラー応答(-1)

# 定時積算電力量計測値の取得
def getIntegralPower(ser, ipv6Addr, unitIntegralPower):
    # 定時積算電力量計測値の取得のコマンドフレーム作成
    cmd = make_echonetlite_command_frame("\xEA") # EPC(参考:EL p.3-7 AppH p.3-275) 定時積算電力量計測値
    
    for i in range(5): # リトライ5回
        # コマンド送信＆結果受信
        line = send_echonetlite_command(ser, ipv6Addr, cmd)

        # 受信結果の確認と変換
        if check_echonetlite_receive(line, "EA") :
            # 内容が定時積算電力量計測値(EA)だったら
            hexYear  = line[-24:-20]
            hexMonth = line[-20:-18]
            hexDay   = line[-18:-16]
            hexHour  = line[-16:-14]
            hexMin   = line[-14:-12]
            hexSec   = line[-12:-10]
            hexPower = line[-10:]
            intYear  = int(hexYear,16)
            intMonth = int(hexMonth,16)
            intDay   = int(hexDay,16)
            intHour  = int(hexHour,16)
            intMin   = int(hexMin,16)
            intSec   = int(hexSec,16)
            intPower = int(hexPower,16)
            logger.debug("定時積算電力量:{0}/{1}/{2} {3}:{4}:{5} {6}kWh".format(intYear,intMonth,intDay,intHour,intMin,intSec,intPower*unitIntegralPower))
            return intYear,intMonth,intDay,intHour,intMin,intSec,int(intPower*unitIntegralPower)
        else:
            time.sleep(1)
    logger.error("定時積算電力量計測値の取得に失敗")
    return -1 # リトライしてだめならエラー応答(-1)








