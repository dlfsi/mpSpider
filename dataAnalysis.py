import SpiderUtils as Su
from Items import BubsItem
from dbOpr import DbOpr as db

from datetime import date, datetime
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import pandas as pd


def getfromdb():
    dbcon=db()
    con=dbcon.con
    cur=con.cursor()
    cur.execute("select * from itemlist")
    rows=cur.fetchall()
    file='item_{dt}.xlsx'
    fname=file.format(dt=date.today().strftime('%Y%m%d'))
    Su.save_to_excel(rows,fname)


def get_stock_price():
    today = date.today()
    end = today.strftime('%Y-%m-%d')
    start = datetime(today.year-1,today.month,today.day)
    quotesdfMS = web.DataReader('MSFT','google',start,end)
    quotesdfITL = web.DataReader('INTC','google',start,end)
    listm=[]
    listy=[]
    for i in range(0, len(quotesdfMS)):
        listm.append(int(quotesdfMS.index[i].strftime('%m'))) #get month just like '02'
        listy.append(int(quotesdfMS.index[i].strftime('%Y')))
    quotesdfMS['month'] = listm
    quotesdfMS['year'] = listy

    listm = []
    listy=[]
    for i in range(0, len(quotesdfITL)):
        listy.append(int(quotesdfMS.index[i].strftime('%Y')))
        listm.append(int(quotesdfITL.index[i].strftime('%m')))  # get month just like '02'
    quotesdfITL['month'] = listm
    quotesdfITL['year'] = listy
    # print(quotesdfMS15.groupby('month').mean().Close)
    MSFT=quotesdfMS['2016-01-01':'2016-12-31']
    ITL=quotesdfITL['2016-01-01':'2016-12-31']
    plt.subplot(211)
    # MSFT.groupby('month').max().Close.plot()
    plt.plot(MSFT,'-.*r')
    plt.subplot(212)
    ITL.groupby('month').max().Close.plot()
    plt.show()

def xlsx_io():
    score=pd.read_excel('data.xlsx')
    sumscore=score['python']+score['math']
    score['sum'] = sumscore
    score.to_excel('data.xlsx')

def practice():
    attrs = ['user id', 'movie id', 'rating', 'timestamp']
    ratings=pd.read_table('ml-100k/u.data',names=attrs)
    attrs = ['user id', 'age', 'gender', 'occupation', 'zip code']
    users=pd.read_table('ml-100k/u.user',names=attrs, delimiter='|')
    attrs = ['movie id','movie title','release date','video release date','IMDb URL','unknown','Action','Adventure','Animation','Childrens','Comedy','Crime','Documentary','Drama','Fantasy','Film-Noir','Horror','Musical','Mystery','Romance','Sci-Fi','Thriller','War','Western']
    # import chardet
    # with open('ml-100k/u.item', 'rb') as f:
    #     result = chardet.detect(f.read())
    movies=pd.read_table('ml-100k/u.item',names=attrs, delimiter='|',encoding='ISO-8859-1')
    mldata = pd.merge(pd.merge(ratings, users), movies)
    # mean_ratings = mldata.pivot_table('rating', index='movie title', columns=['gender'], aggfunc='mean')
    mean_ratings = mldata.pivot_table('rating', index='gender', aggfunc='std')
    # mean_ratings['diff'] = mean_ratings['M'] - mean_ratings['F']
    print(mean_ratings)
    # print(mean_ratings['F'].mean())
    # print(mean_ratings['M'].mean())


def test():
    today = date.today()
    end = today.strftime('%Y-%m-%d')
    start = datetime(today.year-1,today.month,today.day)
    quotesdfMS = web.DataReader('MSFT','google','2014-01-01','2014-12-31')
    # quotesdfITL = web.DataReader('INTC','google',start,end)
    listm=[]
    for i in range(0, len(quotesdfMS)):
        listm.append(int(quotesdfMS.index[i].strftime('%m'))) #get month just like '02'
    quotesdfMS['month'] = listm
    openMS = quotesdfMS.groupby('month').mean().Open
    listopen = []
    for i in range(1, 13):
        listopen.append(openMS[i])
    # plt.plot(openMS.index, listopen)
    # plt.xlabel('Month')
    # plt.ylabel('Average Open Price')
    # plt.title(' Stock Statistics of Microsoft')
    openMS.plot()
    quotesINT = web.DataReader('INTC', 'google', '2014-01-01','2014-12-31')
    quotesINT.Open.plot()
    compdf = pd.DataFrame()
    compdf['MS'] = quotesdfMS.Open
    compdf['INTEL'] = quotesINT.Open
    compdf.plot(title='open price of MS and INTEL')
    plt.scatter(quotesdfMS.Close - quotesdfMS.Open, quotesdfMS.Volume)
    plt.show()

getfromdb()