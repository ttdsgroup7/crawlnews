This project prefer to use anaconda to execute.
Command:
  1. scrapy crawl BBC_news
  2. python console_run.py
  3. nohup python -u console_run.py > dailyspider.log 2>&1 &
1 will start the crawler once.
2 will start the crawler and run every 12 hours
3 will start 2 in the background.

requirements:
conda env create -f BBC-spider.yml
conda activate TTDS-spider  
