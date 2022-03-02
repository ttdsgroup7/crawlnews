from scrapy import cmdline
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler

name = 'BBC_news'
cmd1 = 'scrapy crawl {0} '.format(name)
def crawler_command():
    cmdline.execute(cmd1.split())


if __name__ == '__main__':
    scheduler = BlockingScheduler(timezone="Europe/London")
    scheduler.add_job(crawler_command, 'interval', hours=12, id='test_job1',next_run_time=datetime.datetime.now())
    scheduler.start()

