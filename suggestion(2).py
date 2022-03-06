import nltk
from nltk.collocations import *
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import stopwords
import MySQLdb
import sys, getopt, time
tokenizer = WordPunctTokenizer()
bigram = nltk.collocations.BigramAssocMeasures()
trigram = nltk.collocations.TrigramAssocMeasures()
stop = set(stopwords.words('english'))
db = MySQLdb.connect("34.89.114.242", "root", "!ttds2021", "TTDS_group7", port = 3306)
cursor = db.cursor()
def get_tokenize(s):
    token = tokenizer.tokenize(s)
    return [i for i in token if i not in stop and i.isalpha()]

def get_bigram(s):
    bigram_finder = BigramCollocationFinder.from_words(s)
    score = bigram_finder.score_ngrams(bigram.raw_freq)
    bilist = [i for i, j in score]
    result = [" ".join(i) for i in bilist]
    return result
        
def get_trigram(s):
    trigram_finder = TrigramCollocationFinder.from_words(s)
    score = trigram_finder.score_ngrams(trigram.raw_freq)
    trilist = [i for i, j in score]
    result = [" ".join(i) for i in trilist]
    return result

def update():
    try:
        cursor.execute("delete from suggestion")
        db.commit()
    except:
        print("update failed!")
        db.rollback()
        return
    result = {}
    cursor.execute("select head_line from news order by publish_date desc limit 100")
    titlelist = cursor.fetchall()
    for each in titlelist:
        s = get_tokenize(each[0])
        for each_s in s:
            result[each_s] = result.get(each_s, 0) + 1
        s = get_bigram(s)
        for each_s in s:
            result[each_s] = result.get(each_s, 0) + 1
    for each in result:
        com = "insert into suggestion(key_word, number) values ('%s', %d)" % (each, result[each])
        try:
            cursor.execute(com)
            db.commit()
            print(each, "update!")
        except Exception as s:
            print(s)
            print(each, "failed!")
            db.rollback()
    print("Finish updating suggestions!")

def get_suggestion(key):
    com = "select key_word from suggestion where key_word like '%" + key +"%' order by number desc limit 10"
    cursor.execute(com)
    r = cursor.fetchall()
    return [i[0] for i in r] 
    
    
if __name__ == "__main__":
    while True:
        update()
        time.sleep(86400)

"""    
if __name__ == "__main__":
    info = "python suggest.py [-h] [-u] [-s <keyword>]"
    if len(sys.argv) == 1:
        print(info)
        exit(0)
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hus:")
    except Exception as s:
        print(info)
        exit(0)
    
    try:
        for opt, arg in opts:
            if opt == "-h":
                print(info)
            elif opt == "-u":
                update()
            elif opt == "-s":
                if not arg:
                    raise
                else:
                    print(get_suggestion(arg))
            else:
                raise
    except:
        print(info)
"""
                
    
