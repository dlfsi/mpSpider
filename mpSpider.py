# coding: gbk
from Parser import TmallParser
from Parser import JdParser
from Parser import KaolaParser
from multiprocessing import Process


def spider_handler(source):
    if source == 'tmall':
        tmall = TmallParser()
        tmall.parser()
    elif source == 'jd':
        jd = JdParser()
        item = jd.parser()
    elif source == 'kaola':
        kaola = KaolaParser()
        item = kaola.parser()
    else:
        print('invalid source')
        return False

    return True


if __name__ == "__main__":
    ptmall = Process(target = spider_handler, args=('tmall',))
    # pjd = Process(target = spider_handler, args=('jd',))
    # pkaola = Process(target = spider_handler, args=('kaola',))

    ptmall.start()
    # pjd.start()
    # pkaola.start()

    ptmall.join()
    # pjd.join()
    # pkaola.join()
    print('---------- end ------------')