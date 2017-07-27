from mpSpider import MpSpider
import re
from Items import BubsItem
from scrapy.selector import Selector
import SpiderUtils as Su
from bs4 import BeautifulSoup


class JdParser(MpSpider):
    def __init__(self):
        MpSpider.__init__()
        _nextPage = 44

    def get_search_page(self):
        self.browser.get(self._firstPage)
        pageContent = self.browser.page_source
        # save page source into a file
        # Su.write_to_file('jdSearchPage.html', pageContent)
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
            prdItem.date.append(self._data_time)

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
            prdItem.date.append(self.data_time)

            if item.shopName[idx] == '':
                prdItem.prdSales.append(item.prdSales[idx])
            else:
                pitem = self.parsePrdPage(content, prdItem, item.source[idx])

        self.browser.close()
        # self.conn.addItem(pitem)
        return pitem

    def parsePrdPage(self, content, prdItem, source):
        # parse item by xpath
        content = Selector(text=content)
        if source == 'Tmall':
            prdItem.prdSales.append(content.xpath('//*[@id="J_DetailMeta"]/div[1]/div[1]/div/ul/li[1]/div/span[2]/text()').get())
        else:
            prdItem.prdSales.append(content.xpath('//*[@id="J_SellCounter"]/text()').get())
            # prdItem.shopName.append(content.xpath('//*[@id="J_ShopInfo"]/div/div[1]/div[1]/dl/dd/strong/a/text()').get())
        return prdItem