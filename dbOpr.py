import psycopg2


# class BubsItem():
#
#     def __init__(self):
#         self.prdId = []
#         self.prdName = []
#         self.prdPrice = []
#         self.prdSales = []
#         self.shopName = []
#         self.prdUrl = []
#         self.source = []
#         self.date = []

class DbOpr:

    def __init__(self):
        self.con = self.connect()

    def connect(self):
        return psycopg2.connect(database='tmall', user='joe', password='a')

    def addItemList(self, item):
        cur = self.con.cursor()
        for idx, id in enumerate(item.prdId):
            cur.execute('INSERT INTO ITEMLIST (ITEMID, ITEMNAME, ITEMPRICE, SALESVOLUME, SHOPNAME, ITEMURL, \
                ITEMSOURCE, DATADT) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)', (item.prdId[idx],item.prdName[idx],item.prdPrice[idx],item.prdSales[idx],item.shopName[idx],item.prdUrl[idx],item.source[idx],item.date[idx]))
        self.con.commit()
        return

    def addItem(self, item):
        cur = self.con.cursor()
        for idx, id in enumerate(item.prdId):
            try:
                cur.execute('INSERT INTO ITEM (ITEMID, ITEMNAME, ITEMPRICE, SALESVOLUME, SHOPNAME, ITEMURL, \
                ITEMSOURCE, DATADT) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s)', (item.prdId[idx],item.prdName[idx],item.prdPrice[idx],item.prdSales[idx],item.shopName[idx],item.prdUrl[idx],item.source[idx],item.date[idx]))
            except psycopg2.DataError as e:
                print('Error %s' % e)
                continue
        self.con.commit()

        return

    def queryItem(self, datadt):
        cur = self.con.cursor()
        cur.execute('SELECT * FROM ITEMLIST WHERE DATADT = %s and salesvolume!=0', datadt)
        rows = cur.fetchall()
        return rows

# if __name__ == "__main__":
#     db=dbOpr()
#     item=BubsItem()
#     item.prdId='553684079014'
#     item.prdName='直邮澳洲陆杰喜推荐 Bubs婴儿配方羊奶粉3段12-36个月800g*2罐'
#     item.prdPrice=560
#     item.prdSales=12
#     item.shopName='jessicassuitcase海外旗舰'
#     item.prdUrl='https://detail.tmall.com/item.htm?id=553684079014&ad_id=&am_id=&cm_id=140105335569ed55e27b&pm_id=&abbucket=0'
#     item.source='Tmall'
#     item.date='20170721'
#     db.addItem(item)
#     db.con.close()
