# coding: gbk
from Parser import TmallParser
from Parser import JdParser
from Parser import KaolaParser
from multiprocessing import Process


def spider_handler(source):
    if source == 'tmall':
        tmall = TmallParser()
        tmall.parser(source)
    elif source == 'jd':
        jd = JdParser()
        jd.parser(source)
    elif source == 'kaola':
        kaola = KaolaParser()
        kaola.parser(source)
    else:
        print('invalid source')
        return False

    return True


if __name__ == "__main__":
    spiders = ['tmall','jd','kaola']
    for cnt, spider in enumerate(spiders):
        sprocessing = Process(target=spider_handler, args=(spider,))
        sprocessing.start()