import requests
from openpyxl import Workbook
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
def get_info(ws, q, fro, page, size, typ = "article"):
    """获取以q为关键词某一页的所有信息"""
    web_url = url % (q, size, typ, fro, page)
    result = requests.get(web_url)
    result = result.json()
    news_list = result["result"]    
    #print(news_list[5])
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
        if theme not in themedic:
            print(theme, fro, page)
            theme = "world"
        theme = themedic[theme]
        ws.append((date, title, body, country, image, theme, news_url))
    

def get_info_thread(q, fro, page, size = 10):
    p = fro // 10 + 1
    wb = Workbook()
    ws = wb.active
    ws.append(("date", "title", "content", "country", "image", "theme", "url"))
    name = "%s_%d_%d.xlsx" % (q, fro, page)
    while page > 0:
        #print(p)
        page -= 1
        get_info(ws, q, fro, p, size)
        fro = fro + size
        p += 1
    wb.save(name)
    
        

if __name__ == "__main__":
    get_info_thread("news", 0, 1005)
    
