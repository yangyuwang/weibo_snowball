# -*- coding: utf-8 -*-
import datetime
import json
import os.path
import time
import re

class JsonWriterPipeline(object):
    """
    写入json文件的pipline
    """

    def __init__(self):
        self.file = None
        if not os.path.exists('output_spider'):
            os.mkdir('output_spider')

    def process_item(self, item, spider):
        """
        处理item
        """
        with open("step2_crawler/users_ids.txt","r") as f:
            user_ids=[re.sub("\n","",i) for i in f.readlines()]

        if not self.file:
            now = datetime.datetime.now()
            file_name = spider.name + "_" + str(user_ids[0])+ "-"+ str(user_ids[-1]) + "_" + now.strftime("%Y%m%d%H%M%S") +'.jsonl'
            self.file = open(f'output_spider/{file_name}', 'wt', encoding='utf-8')
        item['crawl_time'] = int(time.time())
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(line)
        self.file.flush()
        return item
