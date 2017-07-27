import re
import time
import SpiderUtils as Su
from Items import BubsItem
from bs4 import BeautifulSoup
from dbOpr import DbOpr as db
from selenium import webdriver
from scrapy.selector import Selector


class MpSpider:
    _urlHead = 'https:'
    pageIndex = 0
    firstPage = ''
    _startUrls = {
        'tmall': 'https://s.taobao.com/search?initiative_id=staobaoz_20170725&q=Bubs&s={idx}',
        'jd': 'https://search.jd.com/Search?keyword=Bubs&enc=utf-8'
    }
    blockLists = [
        '澳洲名品海外专营店','中国国际图书专营店','北京进出口图书专营','cafe24海外旗舰店',
        '易淘商贸11', '易淘商贸12', '易淘商贸14', '可可百货购物商城', '小包子1985',
        '上海慕莎电子商务有限公司', '上海欧美速递', '小梦想欧美时尚','燕子翎儿',
        'sleepwell_baby', '宝贝熊海外专营店'
    ]
    _nextPage = 44

    def __init__(self, source=None):
        # super(MpSpider,self).__init__()
        self._data_dt = time.strftime('%Y%m%d', time.localtime())
        if source is None:
            return
        else:
            self.firstPage = self._startUrls[source]
        self.browser = webdriver.Chrome("chromedriver")
        self._dbcon = db()

    def parser(self):
        item = BubsItem()
        while True:
            response = self.get_search_page()
            if response is None:
                break
            cpages, tpages = self.getTotalPages(response)
            item = self.parseSeachPage(response, item)
            if cpages == tpages:
                break
            else:
                self.pageIndex += self._nextPage
        # log search page information into the database
        # self._dbcon.addItemList(item)
        # parse more details via item page
        pitem = self.itemParser(item)
        # pitem = tmall._dbcon.queryItem()
        # Su.save_to_excel(pitem, 'item_tmall.xlsx')
        return pitem


class TmallParser(MpSpider):
    def __init__(self,*args, **kwargs):
        super(TmallParser,self).__init__(source='tmall',*args, **kwargs)

    def get_search_page(self):
        mode = 'W'
        # access search page
        if mode == 'W':
            url = self.firstPage.format(idx=self.pageIndex)
            self.browser.get(url)
            pageContent = self.browser.page_source
            # save page source into a file
            # Su.write_to_file('searchPage.html', pageContent)
        elif mode == 'F':
            pageContent = Su.read_from_file('searchPage.html')
        elif mode == 'D':
            pageContent = self._dbcon.queryItem(self._data_dt)
        else:
            print('Error: Invalid Acces Mode')
            return

        return pageContent

    def getTotalPages(self, content):
        bscontent = Selector(text=content)
        pageStr = bscontent.xpath('//*[@id="J_relative"]/div[1]/div/div[2]/ul/li[2]/span/text()').get()
        cpages = int(pageStr)
        pageStr = bscontent.xpath('//*[@id="J_relative"]/div[1]/div/div[2]/ul/li[2]/text()').get()
        tpages = int(re.findall('\d+', pageStr)[0])
        return cpages, tpages

    def parseSeachPage(self, content, prdItem):
        bsContent = BeautifulSoup(content, 'lxml')

        for tagSales in bsContent.find_all(attrs={'class': 'deal-cnt'}):
            dealCnt = re.findall(r'\d+', tagSales.text)[0]
            prdItem.prdSales.append(dealCnt)
            prdItem.date.append(self._data_dt)

        for tagStatus in bsContent.find_all(attrs={'class': 'row row-2 title'}):
            prdItem.prdPrice.append(tagStatus.contents[1]['trace-price'])
            prdItem.prdId.append(tagStatus.contents[1]['data-nid'])
            prdItem.prdName.append(tagStatus.contents[1].text)
            itemUrl = tagStatus.contents[1]['href']
            prdItem.prdUrl.append(self._urlHead + itemUrl)
            if str(itemUrl).__contains__('tmall'):
                prdItem.source.append('Tmall')
            elif str(itemUrl).__contains__('taobao'):
                prdItem.source.append('Taobao')
            else:
                prdItem.source.append('Unknown')

        for tagName in bsContent.find_all(attrs={'class': 'row row-3 g-clearfix'}):
            prdItem.shopName.append(tagName.contents[1].text.strip('\t\n '))

        return prdItem

    def itemParser(self, item):
        prdItem = BubsItem()
        # parse detail product information
        for idx, prd in enumerate(item.prdId):
            # if it comes from an invalid shop, then ignore
            if item.shopName[idx] in self.blockLists:
                continue

            # if sales volume is zero, then ignore
            if item.prdSales[idx] == '0':
                continue

            if item.source[idx] == 'Unknown':
                continue

            self.browser.get(item.prdUrl[idx])
            content = self.browser.page_source  # received in string
            prdItem.prdId.append(prd)
            prdItem.shopName.append(item.shopName[idx])
            prdItem.prdUrl.append(item.prdUrl[idx])
            prdItem.source.append(item.source[idx])
            prdItem.prdName.append(item.prdName[idx])
            prdItem.prdPrice.append(item.prdPrice[idx])
            prdItem.date.append(self._data_dt)

            if item.shopName[idx] == '':
                prdItem.prdSales.append(item.prdSales[idx])
            else:
                self.parsePrdPage(content, prdItem, item.source[idx])

        self.browser.close()
        self._dbcon.addItem(prdItem)
        return prdItem

    def parsePrdPage(self, content, prdItem, source):
        # parse item by xpath
        content = Selector(text=content)
        if source == 'Tmall':
            prdItem.prdSales.append(content.xpath('//*[@id="J_DetailMeta"]/div[1]/div[1]/div/ul/li[1]/div/span[2]/text()').get())
        elif source=='Taobao':
            prdItem.prdSales.append(content.xpath('//*[@id="J_SellCounter"]/text()').get())
            # prdItem.shopName.append(content.xpath('//*[@id="J_ShopInfo"]/div/div[1]/div[1]/dl/dd/strong/a/text()').get())
        else:
            return
        return prdItem


class JdParser(MpSpider):
    def __init__(self,*args, **kwargs):
        super(JdParser,self).__init__(source='jd',*args, **kwargs)

    def get_search_page(self):
        self.browser.get(self.firstPage)
        pageContent = self.browser.page_source
        # save page source into a file
        Su.write_to_file('jdSearchPage.html', pageContent)
        return pageContent

    def getTotalPages(self, content):
        bscontent = Selector(text=content)
        cpages = bscontent.xpath('//*[@id="J_topPage"]/span/b/text()').get()
        tpages = bscontent.xpath('//*[@id="J_topPage"]/span/i/text()').get()
        return cpages, tpages

    def parseSeachPage(self, content, prdItem):
        bsContent = BeautifulSoup(content, 'lxml')
        for tagId in bsContent.find_all('li', class_='gl-item'):
            prdItem.prdId.append(tagId['data-sku'])

        for tag in bsContent.find_all('div', class_='gl-i-wrap'):
            prdItem.prdPrice.append(float(tag.contents[3].i.text))

            prdItem.prdName.append(tag.contents[5].em.text)       # product name
            sales = re.findall(r'\d+',tag.contents[7].a.text)    # sales
            prdItem.prdSales.append(int(sales[0]))

            shopName = tag.contents[9].a
            if shopName is None:
                prdItem.shopName.append('')
            else:
                prdItem.shopName.append(shopName.text)            # shop name

            itemUrl = tag.contents[1].a['href']                  # url
            prdItem.prdUrl.append(self._urlHead + itemUrl)

            prdItem.date.append(self._data_dt)
            prdItem.source.append('JD')

        return prdItem

    def itemParser(self, item):
        prdItem = BubsItem()
        # parse detail product information
        for idx, prd in enumerate(item.prdId):
            # if it comes from an invalid shop, then ignore
            if item.shopName[idx] in self.blockLists:
                continue

            # if sales volume is zero, then ignore
            if item.prdSales[idx] == 0:
                continue

            if item.source[idx] == 'Unknown':
                continue

            self.browser.get(item.prdUrl[idx])
            content = self.browser.page_source  # received in string
            prdItem.prdId.append(prd)
            prdItem.prdUrl.append(item.prdUrl[idx])
            prdItem.source.append(item.source[idx])
            prdItem.prdName.append(item.prdName[idx])
            prdItem.prdPrice.append(item.prdPrice[idx])
            prdItem.date.append(self._data_dt)

            content = Selector(text=content)
            if item.shopName[idx] == '':
                prdItem.shopName.append(content.xpath('//*[@id="item-detail"]/div[1]/ul/li[3]/a/text()').get())
            else:
                prdItem.shopName.append(item.shopName[idx])

            sales = content.xpath('//*[@id="comments-list"]/div[1]/div[1]/ul/li[1]/a/em/text()').get()
            nsales = re.findall(r'\d+',sales)
            prdItem.prdSales.append(int(nsales[0]))

        self.browser.close()
        self._dbcon.addItem(prdItem)
        return prdItem


class KaolaParser(MpSpider):
    pass