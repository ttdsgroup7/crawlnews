# -*- coding: utf-8 -*-
import pymysql
from transformers import PegasusForConditionalGeneration, PegasusTokenizer
import torch
from transformers import BartForConditionalGeneration, BartTokenizer
from collections import defaultdict


# model_name = "sshleifer/distilbart-cnn-12-6"
# model_name = "./distilbart-cnn-12-6"

def connectMysql():
    connMysql = pymysql.connect(
        host='34.89.114.242',
        port=3306,
        user='root',
        password='!ttds2021',
        db='TTDS_group7',
        charset='utf8mb4'
    )
    return connMysql


def execute(id, res, curindex=0):
    # print("abstract: ", res[0])
    # print("id: ",id[curindex])
    sentence = 'update news set news_abstract=(%s) where id = (%s)'
    commitlist = []
    for index in range(len(res)):
        commitlist.append((res[index], id[index + curindex]))
    conn = connectMysql()
    cursor = conn.cursor()
    cursor.executemany(sentence, commitlist)
    conn.commit()
    conn.close()
    return len(res)


class Abstraction_Generation():
    src_text = defaultdict(list)
    idlist = []
    res = []
    part = 0
    curindex = 0
    # device = 'cuda' if torch.cuda.is_available() else 'cpu'
    device = 'cuda' if torch.cuda.is_available() else 'cpu'

    def __init__(self, text):
        cnt = 0
        s = list(text.values())
        for i in s:
            # reduce cnt if GPU RAM not enough
            # 30 lines/part costs about 12GB GPU RAM, for k80
            # 40 for tesla t4
            if cnt < 30:
                cnt += 1
            else:
                self.part += 1
                cnt = 1
            # @ is shown in results, not useful, delete it
            self.src_text[self.part].append(i.replace('@', ''))
        self.idlist = list(text.keys())

    # xsum used to generate one sentence, ideal for title prediction,  too short for abstaction
    def Pegasus(self):
        model_name = 'google/pegasus-xsum'  # 'google/pegasus-large'
        from transformers import PegasusForConditionalGeneration, PegasusTokenizer
        tokenizer = PegasusTokenizer.from_pretrained(model_name)
        model = PegasusForConditionalGeneration.from_pretrained(model_name).to(self.device)
        batch = tokenizer(self.src_text, truncation=True, padding='longest', return_tensors="pt").to(self.device)
        # model.generate(batch['input_ids'],max_length=...,min_length=...)
        # length is sum of token, not words
        translated = model.generate(**batch, min_length=30, max_length=100)
        return tokenizer.batch_decode(translated, skip_special_tokens=True)

    # generate several sentences, ideal for abstraction
    # BART is pre-trained by (1) corrupting text with an arbitrary noising function, and (2) learning a model to reconstruct the original text.
    def Bart(self):
        # facebook/bart-base 2.1GB
        # distilbart-xsum-12-1 400MB
        # https://huggingface.co/sshleifer/distilbart-cnn-12-6 speed
        model_name = "./distilbart-cnn-12-6"
        tokenizer = BartTokenizer.from_pretrained(model_name)
        # forced_bos_token_id =0 disable support for multilingual models
        model = BartForConditionalGeneration.from_pretrained(model_name, forced_bos_token_id=0).to(self.device)
        for i in range(self.part + 1):
            print("part {} start".format(i))
            batch = tokenizer(self.src_text[i], truncation=True, padding='longest', return_tensors='pt').to(self.device)
            translated = model.generate(batch['input_ids'], min_length=50, max_length=100)
            # same effect
            # print([tokenizer.decode(g, skip_special_tokens=True, clean_up_tokenization_spaces=False) for g in translated])
            self.res.extend(
                tokenizer.batch_decode(translated, skip_special_tokens=True, clean_up_tokenization_spaces=False))
            # update every 50 blocks, reduce crash expense
            if not i % 50:
                self.curindex += execute(self.idlist, self.res, self.curindex)
                self.res.clear()
        execute(self.idlist, self.res, self.curindex)
        return self.res

    # used to predict words with tags <mask>, can be deployed in the future
    def fill_mask(self):
        model = BartForConditionalGeneration.from_pretrained("facebook/bart-large", forced_bos_token_id=0)
        tok = BartTokenizer.from_pretrained("facebook/bart-large")
        example_english_phrase = "My friends are <mask> but they eat too many carbs."
        batch = tok(example_english_phrase, return_tensors='pt')['input_ids']
        logits = model(batch).logits
        # find index
        mask = (batch[0] == tok.mask_token_id).nonzero().item()
        probs = logits[0, mask].softmax(dim=0)
        values, predictions = probs.topk(5)
        print(tok.decode(predictions).split())
        # batch = tok(example_english_phrase, return_tensors='pt')
        # generated_ids = model.generate(batch['input_ids'])
        # return tok.batch_decode(generated_ids, skip_special_tokens=True)

def get_content():
    conn = connectMysql()
    cursor = conn.cursor()
    sentence = 'select id,content from news where news_abstract is NULL'
    cursor.execute(sentence)
    text = cursor.fetchall()
    conn.close()
    return text

if __name__ == '__main__':
    text = dict(get_content())
    test = Abstraction_Generation(text)
    res = test.Bart()
    print('success')
