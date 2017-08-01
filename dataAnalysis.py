import SpiderUtils as Su
from Items import BubsItem
from dbOpr import DbOpr as db

from datetime import date, datetime
import pandas_datareader.data as web


def getfromdb():
    dbcon=db()
    pitem=BubsItem()
    cur=dbcon.cursor()
    cur.dbcon.con.cursor()
    cur.execute('select * from item')
    rows=cur.fetchall()
    Su.save_to_excel(rows,'item.xlsx')


today = date.today()
end = today.strftime('%Y-%m-%d')
start = datetime(today.year-1,today.month,today.day)
quotesMS = web.DataReader('MSFT','google',start,end)
quotesdfMS = quotesMS
list = []
quotesdfMS15 = quotesdfMS['2017/01/01':'2017/12/31']
for i in range(0, len(quotesdfMS15)):
    list.append(int(quotesdfMS15.index[i].strftime('%m'))) #get month just like '02'
quotesdfMS15['month'] = list
print(quotesdfMS15.groupby('month').mean().Close)