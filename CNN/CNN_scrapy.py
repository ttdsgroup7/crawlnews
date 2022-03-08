import requests
import MySQLdb
import sys, getopt
import time
headers = {
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://edition.cnn.com',
            'pragma': 'no-cache',
            'referer': 'https://edition.cnn.com/',
            'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'
            }
url = "https://search.api.cnn.io/content?q=%s&size=%d&type=%s&from=%d&page=%d"
themedic = {"business": "business", "climate": "climate", "coronavirus": "coronavirus", "education": "education",
             "entertainment": "entertainment", "health": "health", "politics": "politics", "science": "science",
             "tech": "tech", "world": "world", "sports": "sports", "travel": "travel", "media": "entertainment",
             "architecture": "business", "sport": "sports", "economy": "business", "investing": "business", "tennis": "sports",
             "golf": "sports", "cnn10": "entertainment", "fashion": "entertainment", "design": "business", "weather": "climate",
             "india": "business", "success": "business", "homes": "business", "art": "entertainment", "football": "sports",
             "car": "entertainment", "foodanddrink": "entertainment", "motorsport": "sports", "business-food": "entertainment",
             "culture": "entertainment", "beauty": "entertainment", "travel-stay": "travel", "luxury": "entertainment"}
db = MySQLdb.connect("34.89.114.242", "root", "!ttds2021", "TTDS_group7", port = 3306,charset='utf8')
cursor = db.cursor()
countrydir = {'Asia':'Asia',
              'Middleeast': "Middle East",
              'Africa': 'Africa',
              'US': "US&Canada",
              'Europe': 'Europe'}
com1 = "insert into news(id, publish_date, head_line, \
       content, country, image, theme, url) values(%d, \
       str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'), %s, %s, %s, %s, %s, %s)"
com2 = "insert into news(id, publish_date, head_line, \
       content, image, theme, url) values(%d, \
       str_to_date(%s,'%%Y-%%m-%%d %%H:%%i:%%s'), %s, %s, %s, %s, %s)"

def get_info(q, fro, page, size, typ = "article"):
    """获取以q为关键词某一页的所有信息"""
    web_url = url % (q, size, typ, fro, page)
    result = requests.get(web_url)
    result = result.json()
    news_list = result["result"]    
    #print(news_list[5])
    r = []
    for each in news_list:
        body = each["body"]
        title = each["headline"]
        date = each["lastPublishDate"]
        mapped_section = each["mappedSection"]
        theme = each["section"]
        image = each["thumbnail"]
        news_url = each["url"]
        if theme == "cnn10":
            continue
        if mapped_section == "WORLD":
            if theme != "world":
                if theme == "us":
                    country = "US"
                elif theme == "uk":
                    country = "UK"
                else:
                    country = theme.capitalize()
            else:
                country = ""
        elif mapped_section == "US":
            country = "US"
        elif not mapped_section:
            if theme == "americas":
                country = "US"
            else:
                country = ""
        else:
            country = ""
        theme = themedic.get(theme, "world")
        if theme != "world":
            country = ""
        country = countrydir.get(country, "")
        date = date[:19].replace("T", " ")
        r.append((date, title, body, country, image, theme, news_url))
    return r

def get_info_thread(q, fro, page, size):
    p = fro // 10 + 1
    cursor.execute("select max(id) from news")
    i = cursor.fetchall()
    if not i:
        i = 1
    else:
        i = i[0][0] + 1
    print("begin id:", i)
    while page > 0:
        page -= 1
        r = get_info(q, fro, p, size)
        fro = fro + size
        p += 1
        for date, title, body, country, image, theme, news_url in r:
            success = send_sql(i, date, title, body, country, image, theme, news_url)
            if success:
                i += 1
    print("end id:", i - 1)

def send_sql(i, date, title, body, country, image, theme, news_url):
    e = cursor.execute("select id from news where url=" + repr(news_url))
    if len(body)>65535:
        return
    if e != 0:
        print('"%s" exists!' % title)
        return False
    if not country:
        com = com2 % (i, repr(date), repr(title), repr(body), repr(image), repr(theme), repr(news_url))
    else:
        com = com1 % (i, repr(date), repr(title), repr(body), repr(country), repr(image), repr(theme), repr(news_url))
    try:
        cursor.execute(com)
        db.commit()
        print("id: %d finish!" % i)
        return True
    except Exception as s:
        print(s)
        print(com)
        db.rollback()
        return False

if __name__ == "__main__":
    info = """python CNN_scrapy.py [-h] [-q <key words>] [-f <beginning number>] [-p <page number>] [-s <getting size>]
                              -q default: news
                              -f default: 0
                              -p default: 500
                              -s default: 10"""
    q = "news"
    f = 0
    p = 500
    s = 10
    argvlist = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argvlist, "hq:f:p:s:")
    except Exception as s:
        print(info)
        exit(0)
    try:
        for opt, arg in opts:
            if opt == "-h":
                print(info)
                exit(0)
            elif opt == "-q":
                q = arg
            elif opt == "-f":
                f = int(arg)
                if f < 0:
                    raise
            elif opt == "-p":
                p = int(arg)
                if p < 0:
                    raise
            elif opt == "-s":
                s = int(arg)
                if s < 0:
                    raise
    except Exception as s:
        print(info)
        exit(0)
    while True:
        get_info_thread(q, f, p, s)
        time.sleep(43200)
        
    
    

    
    
    
