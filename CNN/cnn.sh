#!/bin/bash

# conda remove --name spider --all
# conda env create -f environment.yml
# sleep(15)
conda activate spider
sleep(5)
python CNN_scrapy.py
