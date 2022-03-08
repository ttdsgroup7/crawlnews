#from scrapy import cmdline
import os
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import time

name = 'BBC_news'
cmd1 = 'scrapy crawl {0} '.format(name)
def crawler_command():
    time_now = time.time()
    global cmd1
    cmd1 = cmd1 + "-s LOG_FILE={0}.log".format(time_now)
    os.system(cmd1)
    #cmdline.execute(cmd1.split())


if __name__ == '__main__':
    #scheduler = BlockingScheduler(timezone="Europe/London")
    #scheduler.add_job(crawler_command, 'interval', hours=12, id='test_job1',next_run_time=datetime.datetime.now())
    #scheduler.start()
    while True:
        crawler_command()
        time.sleep(43200)
