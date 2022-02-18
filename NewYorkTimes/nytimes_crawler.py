import sys

from settings.dataset_conf import DatasetConfiguration
from article.nytimes_article import NytimeArticleFetcher
import datetime
import time

def is_valid_date(date):
    for i in date[1:]:
        try:
            time.strptime(i, '%Y-%m-%d')
        except:
            return False
    if len(date) ==3 and time.strptime(date[1], '%Y-%m-%d')>time.strptime(date[2], '%Y-%m-%d'):
        return False
    return True

if __name__ == '__main__':
    cur = datetime.datetime.now().isoformat()[:10]
    yesterday = (datetime.datetime.now() + datetime.timedelta(days=-1)).isoformat()[:10]
    config = DatasetConfiguration()
    length = len(sys.argv)
    if sys.argv[-1] =='&':
        length-=1
    if length ==1:
        config.load('./settings/nytimes.cfg',yesterday,cur)
        print("From {} to {}".format(yesterday,cur))
    elif length==2 and is_valid_date(sys.argv):
        config.load('./settings/nytimes.cfg',sys.argv[1],cur)
        print("From {} to {}".format(sys.argv[1], cur))
    elif length==3 and is_valid_date(sys.argv):
        config.load('./settings/nytimes.cfg',sys.argv[1],sys.argv[2])
        print("From {} to {}".format(sys.argv[1], sys.argv[2]))
    else:
        print('wrong input')
        exit()
    nytime_article_fetcher = NytimeArticleFetcher(config)
    nytime_article_fetcher.fetch()
