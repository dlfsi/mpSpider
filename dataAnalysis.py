import SpiderUtils as Su
from Items import BubsItem
from dbOpr import DbOpr as db

from datetime import date, datetime, timedelta
import pandas_datareader.data as web
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


def getfromdb():
    dbcon=db()
    con=dbcon.con
    cur=con.cursor()
    # cur.execute("select * from item where datadt>'20170731'")
    # rows=cur.fetchall()
    # file='item_{dt}.xlsx'
    # fname=file.format(dt=date.today().strftime('%Y%m%d'))
    # Su.save_to_excel(rows,fname)

    td = date.today().strftime('%Y%m%d')
    yd = (date.today() + timedelta(-1)).strftime('%Y%m%d')
    sql = "select a.itemname pname, a.itemprice price, a.salesvolume ydsales, b.salesvolume tdsales, (b.salesvolume-a.salesvolume)*a.itemprice as amount, 'A2' src, '{dt}' datadt from item a, item b where a.datadt='{d1}' and b.datadt='{d2}' and a.itemname=b.itemname and a.itemsource='kaola' and a.itemname like '%a2%' and b.salesvolume>a.salesvolume"
    statements = sql.format(dt=td, d1=yd, d2=td)
    from sqlalchemy import create_engine
    engine = create_engine('postgresql://joe:a@localhost:5432/tmall')
    data = pd.read_sql_query(statements,con)
    # file = r'.\Data\a2_sales_{dt}.xlsx'
    # fname = file.format(dt=date.today().strftime('%Y%m%d'))
    # data.to_excel(fname,sheet_name=td)
    data.to_sql('sales_sum',engine,index=False,if_exists='append')

    sql = "select a.itemname pname, a.itemprice price, a.salesvolume ydsales, b.salesvolume tdsales, (b.salesvolume-a.salesvolume)*a.itemprice as amount, 'Bubs' src, '{dt}' datadt from item a, item b where a.datadt='{d1}' and b.datadt='{d2}' and a.itemname=b.itemname and a.itemsource='kaola' and a.itemname like '%ubs%' and b.salesvolume>a.salesvolume"
    statements = sql.format(dt=td, d1=yd, d2=td)
    data = pd.read_sql_query(statements, con)
    # file = r'.\Data\bubs_sales_{dt}.xlsx'
    # fname = file.format(dt=date.today().strftime('%Y%m%d'))
    # data.to_excel(fname, sheet_name=td)
    data.to_sql('sales_sum',engine,index=False,if_exists='append')


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


def get_quotes():
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

def dbread():
    dbcon = db().con

    klquery = "select * from item where itemsource='kaola'"
    kldf = pd.read_sql(klquery, dbcon)
    kltbl = pd.pivot_table(kldf, index=["itemname"], columns=["datadt"], values=["salesvolume"],aggfunc=np.sum,fill_value=0)
    kltbl.to_excel('.\Data\kaola.xlsx',sheet_name='kaola')

    jdquery = "select * from item where itemsource='JD'"
    jddf = pd.read_sql(jdquery, dbcon)
    jdtbl = pd.pivot_table(jddf, index=["itemname"], columns=["datadt"], values=["salesvolume"],aggfunc=np.sum,fill_value=0)
    jdtbl.to_excel('.\Data\jd.xlsx',sheet_name='jd')

    tmquery = "select * from item where itemsource='Tmall'"
    tmdf = pd.read_sql(tmquery, dbcon)
    tmtbl = pd.pivot_table(tmdf, index=["itemname"], columns=["datadt"], values=["salesvolume"],aggfunc=np.sum,fill_value=0)
    tmtbl.to_excel('.\Data\\tmall.xlsx',sheet_name='tmall')
    tmtbl.plot()
    plt.show()


# dbread()
getfromdb()