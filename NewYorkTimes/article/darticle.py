import sys
import os.path
import json
import time
import datetime
import pymysql

from network.network import NetworkFetcher

theme = {
    'Business': 'business',
    'Health': 'health',
    'Well': 'health',
    'Technology': 'tech',
    'Climate': 'climate',
    'Briefing': 'entertainment',
    'Entertainment': 'entertainment',
    'Science': 'science',
    'Politics': 'politics',
    'Education': 'education',
    'Sports': "world",
    'Arts': 'world'
}

class ArticleFetcher:

    RETRY = 3
    def __init__(self, config):
        self.config = config
        self.download_link_fetcher = None
        self.html_fetcher = NetworkFetcher()
        self.path = config.path
        self.pasturl = self.gethistory()

    def gethistory(self):
        conn = self.connectMysql()
        cursor = conn.cursor()
        sentence = "select url from news  where url like '%nytimes%'"
        cursor.execute(sentence)
        text = cursor.fetchall()
        conn.close()
        return set(i[0] for i in text)

    def connectMysql(self):
        connMysql = pymysql.connect(
            host='34.89.114.242',
            port=3306,
            user='root',
            password='!ttds2021',
            db='TTDS_group7',
            charset='utf8mb4'
        )
        return connMysql

    def execute(self,sentence, commitlist):
        conn = self.connectMysql()
        cursor = conn.cursor()
        cursor.executemany(sentence, commitlist)
        conn.commit()
        conn.close()

    def _html_to_infomation(self, html, link, date):
        return {}

    def _extract_information(self, link, date):
        html = self.html_fetcher.fetch(link)
        if html is None:
            sec = 5
            for _ in range(0, self.RETRY):
                print('Retrying')
                time.sleep(sec)
                html = self.html_fetcher.fetch(link)
                if html is not None:
                    print('Retrying success')
                    break
                #sec+=5
        if html is None:
            print('article ', link, 'failed')
            return None
        return self._html_to_infomation(html, link, date)

    def _lazy_storage(self, links, date):
        total_links = len(links)
        current_link = 1
        articles = list()
        for link in links:
            print('>>> {c} in {t} articles\r'.format(c=current_link, t=total_links), end='')
            current_link += 1
            article = self._extract_information(link, date)
            time.sleep(self.config.sleep)
            if article is not None:
                articles.append(article)
            else:
                self.push(articles)
                articles = []
            if len(articles) > 500:
                self.push(articles)
                articles = []
        self.push(articles)

    def push(self,handle):
        commitlist=[]
        sentence = 'insert IGNORE into news(Publish_date,head_line,content,image,theme,url) values ((%s),(%s),(%s),' \
                   '(%s),(%s),(%s)) '
        last_date = datetime.datetime.now().isoformat()[:10]+' 12:00:00'
        for i in handle:
            # j: (title,published_date,section,content,link,image)
            # tb:(date,title,content,country,image,theme,url)
            if not i['content']:
                continue
            tmp_theme = 'world'
            tmp_date = last_date
            if i['section'] in theme:
                tmp_theme = theme[i['section']]
            if i['published_date'] is not None:
                tmp_date = i['published_date'].replace('T', ' ')[:-5]
            commitlist.append((tmp_date, i['title'], i['content'], i['image'], tmp_theme, i['link']))

        if len(commitlist) > 10000:
            i = 0
            while i < len(commitlist):
                part = commitlist[i:i + 10000]
                self.execute(sentence, part)
                i += 10000
                print("query {} finished".format(i))
        else:
            self.execute(sentence, commitlist)
        print('finished')


    def fetch(self):
        current_date = 1
        while True:
            api_url, date = self.download_link_fetcher.next()
            if api_url is None:
                break
            print(date.strftime('%Y-%m-%d'),
                  '{c} in dates                  '.format(c=current_date))

            links = self.download_link_fetcher.fetch(api_url)
            links = set(links)-self.pasturl
            self._lazy_storage(links, date)
            time.sleep(self.config.sleep)
            print(date.strftime('%Y-%m-%d'),
                  'date {c} finished                 '.format(c=current_date))
            current_date += 1
