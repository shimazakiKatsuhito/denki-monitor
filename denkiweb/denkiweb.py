#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, date, timedelta
import calendar
import _strptime

import denki_db

import logging
import denki_log
logging.basicConfig(
   level=denki_log.log_level,
   format=denki_log.log_format,
   filename=denki_log.log_filename
)
logger = logging.getLogger("DenkiWebLog")
logger.info("Start DenkiWeb System\n")


from flask import Flask, render_template, request, redirect, url_for
app = Flask(__name__)

denki_db.open_db()
 
@app.route('/')
def index():
    row = denki_db.get_InstantaneousPower_now()
    datatime = row[1].strftime("%Y/%m/%d %H:%M")
    datapower = row[2]
    # index.html をレンダリングする
    return render_template('index.html', nowpower=datapower, nowtime=datatime)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.route('/today')
def today_instantaneous_power():
    today = datetime.today().strftime("%Y-%m-%d")
    starttime = today + u" 00:00:00"
    endtime = today + u" 23:59:59"
    todaydata = denki_db.get_InstantaneousPower_period(starttime, endtime)

    yesterday = (datetime.today()-timedelta(days=1)).strftime("%Y-%m-%d")
    starttime = yesterday + u" 00:00:00"
    endtime = yesterday + u" 23:59:59"
    yesterdaydata = denki_db.get_InstantaneousPower_period(starttime, endtime)

    row = denki_db.get_InstantaneousPower_now()
    datatime = row[1].strftime("%Y/%m/%d %H:%M")
    datapower = row[2]

    # index.html をレンダリングする
    return render_template('index.html', graphdata=todaydata, graphdata2=yesterdaydata, nowpower=datapower, nowtime=datatime)

@app.route('/week')
def thisweek_integral_power():
    wdata = denki_db.get_NearWeek_IntegralPower()

    row = denki_db.get_InstantaneousPower_now()
    datatime = row[1].strftime("%Y/%m/%d %H:%M")
    datapower = row[2]

    # index.html をレンダリングする
    return render_template('index.html', graphdata3=wdata, nowpower=datapower, nowtime=datatime, refresh_rate=60*10)

@app.route('/SpecefiedDate/<date>')
def get_SpecefiedDate_IntegralPower(date=None):
    data = denki_db.get_SpecefiedDate_IntegralPower(date)
    msg=date+u"の電気使用量は、"+str(data[2]/10.0)+u"[kWh]です。"

    row = denki_db.get_InstantaneousPower_now()
    datatime = row[1].strftime("%Y/%m/%d %H:%M")
    datapower = row[2]

    # index.html をレンダリングする
    return render_template('index.html', message=msg, nowpower=datapower, nowtime=datatime, refresh_rate=60*10)

@app.route('/dailythismonth')
def get_deilythismonth_integral_power():
    mstart = (datetime.today().replace(day=1)).strftime("%Y-%m-%d")
    mdays = calendar.monthrange(datetime.today().year, datetime.today().month)[1]
    pdata = denki_db.get_Daily_IntegralPower_fromSpecifiedDate(mstart,mdays)

    wdata = []
    day = 0
    # 第1週目
    w1data = []
    wd = pdata[0][1].weekday()
    for i in range(0, wd):
      w1data.append([0,None,0])
    for i in range(wd, 7):
      w1data.append(pdata[day])
      day+=1
    wdata.append(w1data)
    # 第2週目以降
    for n in range(1,5):
      w2data = []
      for i in range(7):
        if(day<mdays):
          w2data.append(pdata[day])
          day+=1
        else:
          w2data.append([0,None,0])
      wdata.append(w2data)

    row = denki_db.get_InstantaneousPower_now()
    datatime = row[1].strftime("%Y/%m/%d %H:%M")
    datapower = row[2]

    # index.html をレンダリングする
    return render_template('index.html', graphdata4=wdata, nowpower=datapower, nowtime=datatime, refresh_rate=60*60)


if __name__ == "__main__":
    app.debug = True # デバッグモード有効化
    app.run(host='0.0.0.0', port=5000) # どこからでもアクセス可能に
