import psycopg2


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
        cur.execute('SELECT * FROM ITEM WHERE DATADT = %s and salesvolume!=0', datadt)
        rows = cur.fetchall()
        return rows
