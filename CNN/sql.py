import MySQLdb
import openpyxl
db = MySQLdb.connect("34.89.114.242", "root", "!ttds2021", "TTDS_group7", port = 3306)
cursor = db.cursor()
wb = openpyxl.load_workbook('news_0_1005.xlsx')
ws = wb["Sheet"]
urllist = []
cursor.execute("select id from news")
r = cursor.fetchall()
r = [i[0] for i in r]
b = max(r)
i = b
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
for row in ws.rows:
       if i == b:
              i += 1
              print("begin id:",i)
              continue
       mid = [i]
       for cell in row:
              mid.append(cell.value)
       if mid[7] in urllist:
              continue
       else:
              urllist.append(mid[7])
       mid[1] = mid[1][:19].replace("T", " ")
       for j in range(len(mid)):
              if type(mid[j]) == str:
                     mid[j] = repr(mid[j])
       
       if mid[4] != None:
              if mid[6] == "world":
                     mid[4] = countrydir[mid[4]]
                     com = com1 % tuple(mid)
              else:
                     mid.pop(4)
                     com = com2 % tuple(mid)
       else:
              mid.pop(4)
              com = com2 % tuple(mid)
       try:
              cursor.execute(com)
              db.commit()
       except Exception as s:
              print(s)
              print(com)
              db.rollback()
              continue
       i += 1
       if i % 100 == 0:
              print(i, "finish")
print("end id:", i - 1)
db.close()
wb.close()
       
