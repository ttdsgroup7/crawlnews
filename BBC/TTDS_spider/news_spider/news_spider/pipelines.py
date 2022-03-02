# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymysql


class mysql_pipeline:

    def process_item(self, item, spider):
        self.insert_mysql(item)
        return item

    # connect to the databases
    def open_spider(self, spider):
        self.conn = pymysql.connect(host='127.0.0.1',
                                    port=3306,
                                    user='root',
                                    password='!ttds2021',
                                    db='TTDS_group7',
                                    charset='utf8mb4')
        self.cursor = self.conn.cursor()
        self.ori_table = 'news'

        # delete_sql = "DROP TABLE IF EXISTS {}".format(self.ori_table)
        # self.cursor.execute(delete_sql)
        # create_sql = """
        # CREATE TABLE BBC_news (
        #     docid INT NOT NULL AUTO_INCREMENT,
        #     publish_date VARCHAR(255),
        #     head_line TINYTEXT,
        #     content TEXT,
        #     tag VARCHAR(255),
        #     PRIMARY KEY (docid),
        #     UNIQUE KEY (tag)
        # )
        # """
        # self.cursor.execute(create_sql)

    # Close the databases
    def close_spider(self, spider):
        print("Terminating" + spider.name + "spider...")
        self.cursor.close()
        self.conn.close()
        # self.db_conn.connection_pool.disconnect()

    # Insert the data
    def insert_mysql(self, item):
        select_sql = '''select * from {0} where url = '{1}' '''.format(self.ori_table, item.get('url'))
        self.cursor.execute(select_sql)
        if not self.cursor.fetchall():
            # print(sql)
            try:
                sql = '''insert ignore into {0}(publish_date, head_line, content, country, image, theme, url)  VALUES ('{1}','{2}','{3}','{4}','{5}','{6}','{7}') ''' \
                    .format(self.ori_table,
                            item.get('publish_time'),
                            pymysql.converters.escape_string(item.get('headline')),
                            pymysql.converters.escape_string(item.get('content')),
                            item.get('location'),
                            item.get('image'),
                            pymysql.converters.escape_string(item.get('related_topic')),
                            item.get('url')
                            )
                self.cursor.execute(sql)
                self.conn.commit()
                print('successfully writing the data')
            except BaseException as e:
                print(e)
                print("error writing sql:" + sql)
        else:
            print("data already inserted")
