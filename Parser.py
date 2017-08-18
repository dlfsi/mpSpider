import re
import time
import math
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
        'tmall': 'https://s.taobao.com/search?initiative_id=staobaoz_{dt}',
        'jd':    'https://search.jd.com/Search?keyword={key}&enc=utf-8',
        'kaola': 'https://www.kaola.com/search.html?zn=top&searchRefer=searchbutton&timestamp={tm}'
    }
    blockLists = [
        '澳洲名品海外专营店','中国国际图书专营店','北京进出口图书专营','cafe24海外旗舰店',
        '易淘商贸11', '易淘商贸12', '易淘商贸14', '可可百货购物商城', '小包子1985',
        '上海慕莎电子商务有限公司', '上海欧美速递', '小梦想欧美时尚','燕子翎儿',
        'sleepwell_baby', '宝贝熊海外专营店'
    ]
    _nextPage = 44
    pgIdx = '&bcoffset=4&p4ppushleft=1,48&ntoffset=4&s={idx}'

    def __init__(self, source=None):
        self._data_dt = time.strftime('%Y%m%d', time.localtime())
        sec, day = math.modf(time.time())
        self._tm = str(int(day)) + str(int(sec*1000))
        self.firstPage = self._startUrls[source]
        if source == 'kaola':
            self.firstPage = self.firstPage.format(tm=self._tm) +'&key={key}'
        elif source == 'tmall':
            self.firstPage = self.firstPage.format(dt=self._data_dt) + '&q={key}'

        self.browser = webdriver.Chrome("chromedriver")
        self._dbcon = db()

    def get_search_page(self, url):
        self.browser.get(url)
        return self.browser.page_source

    def parser(self, source):
        keywords = {'tmall': ['Bubs'],
                    'jd': ['Bubs'],
                    'kaola': ['Bubs', 'A2']
        }
        words = keywords[source]
        for value in words:
            item = BubsItem()
            url = self.firstPage.format(key=value)
            while True:
                response = self.get_search_page(url)
                if response is None:
                    break
                cpages, tpages = self.getTotalPages(response)
                item = self.parseSeachPage(response, item)
                if cpages == tpages:
                    break
                else:
                    self.pageIndex += self._nextPage
            # log search page information into the database
            self._dbcon.addItemList(item)

            # parse more details via item page
            self.itemParser(item)

        return


class TmallParser(MpSpider):
    def __init__(self,*args, **kwargs):
        super(TmallParser,self).__init__(source='tmall',*args, **kwargs)

    def get_search_page(self, url):
        # access search page
        if self.pageIndex == 44:
            url = url + '&bcoffset=4&p4ppushleft=1,48&s=44&ntoffset=4'
        elif self.pageIndex != 0:
            url = url + self.pgIdx.format(idx=self.pageIndex)
        self.browser.get(url)
        return self.browser.page_source

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
            prdItem.prdName.append(tagStatus.contents[1].text.strip('\t\n '))
            itemUrl = tagStatus.contents[1]['href']
            if itemUrl.__contains__('click.simba'):
                prdItem.prdUrl.append(itemUrl)
            else:
                prdItem.prdUrl.append(self._urlHead + itemUrl)
            if itemUrl.__contains__('tmall'):
                prdItem.source.append('Tmall')
            elif itemUrl.__contains__('taobao'):
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
            if item.source[idx]== 'Taobao':
                print('--->%s' % item.prdUrl[idx])
            content = self.browser.page_source  # received in string

            if item.shopName[idx] == '':
                item.source[idx] = 'Douyu'
            prdItem = self.parsePrdPage(content, prdItem, item.source[idx])

            if item.source[idx] == 'Tmall':
                prdItem.shopName.append(item.shopName[idx])
            elif item.source[idx] == 'Douyu':
                prdItem.prdSales.append(item.prdSales[idx])
                prdItem.shopName.append(item.shopName[idx])
            prdItem.prdId.append(prd)
            prdItem.prdUrl.append(item.prdUrl[idx])
            prdItem.source.append(item.source[idx])
            prdItem.prdName.append(item.prdName[idx])
            prdItem.prdPrice.append(item.prdPrice[idx])
            prdItem.date.append(self._data_dt)

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
            prdItem.shopName.append(content.xpath('//*[@id="detail"]/div[2]/div[1]/div/div[2]/div/div[1]/div/div[1]/div[2]/h3/a/text()').get())

        return prdItem


class JdParser(MpSpider):
    def __init__(self,*args, **kwargs):
        super(JdParser,self).__init__(source='jd',*args, **kwargs)

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
    def __init__(self,*args, **kwargs):
        super(KaolaParser,self).__init__(source='kaola',*args, **kwargs)

    def getTotalPages(self, content):
        bsContent = BeautifulSoup(content, 'lxml')
        pStr = bsContent.find('div', class_='simplePage').contents[1].text
        cpages, tpages = pStr.split('/')
        return cpages, tpages

    def parseSeachPage(self, content, prdItem):
        bsContent = BeautifulSoup(content, 'lxml')
        for tag in bsContent.find_all('a', class_='comments'):     # sales
            prdItem.prdSales.append(int(tag.text))
            prdItem.date.append(self._data_dt)
            prdItem.source.append('kaola')

        for tag in bsContent.find_all('p', class_='selfflag'):     # shop name
            prdItem.shopName.append(tag.text.strip('\n'))

        for tag in bsContent.find_all(attrs={'class':'goodswrap'}):
            if len(tag.contents)>=4:
                prdItem.prdPrice.append(float(tag.contents[3].p.span.contents[1]))
                prdItem.prdId.append(tag.contents[1].img['id'].split('-')[2])  # id

                prdItem.prdName.append(tag.contents[3].a['title'])       # product name
                itemUrl = tag.contents[1]['href']                      # url
                prdItem.prdUrl.append(self._urlHead + 'www.kaola.com' + itemUrl)

        return prdItem

    def itemParser(self, item):
        self._dbcon.addItem(item)
