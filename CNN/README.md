## Install Anaconda 
```bash
$ curl -O https://repo.anaconda.com/archive/Anaconda3-2021.11-Linux-x86_64.sh
$ bash Anaconda3-2021.11-Linux-x86_64.sh
$ source ~/.bashrc
```
## Create and Activate Spider environment
```bash
$ conda env create -f environment.yml
$ conda activate spider
```

`environment.yml`
```
name: spider
dependencies:
  - mysqlclient
  - requests
```

## Run spider
```bash
$ python CNN_scrapy.py
```

