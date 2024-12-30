import os
from weibo_escraper import get_weibo_profile
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import json
import re
from spiders.tweet_by_user_id import TweetSpiderByUserID
from spiders.tweet_by_keyword import TweetSpiderByKeyword
from spiders.tweet_by_tweet_id import TweetSpiderByTweetID
from spiders.comment import CommentSpider
from spiders.follower import FollowerSpider
from spiders.user import UserSpider
from spiders.fan import FanSpider
from spiders.repost import RepostSpider
import sys

'''设置 round 值'''
current_round = int(sys.argv[1])

'''路径'''
os.chdir("/Users/pootaatoos/weibo_snowball")

'''环境配置'''
os.environ['SCRAPY_SETTINGS_MODULE'] = 'settings'
settings = get_project_settings()
process = CrawlerProcess(settings)


#user_list & screen_names
'''加载用户ID'''
input_path = "step2_crawler/users_ids.txt" #上一轮最后覆盖保存
try:
    with open(input_path, "r") as f:
        user_list = [re.sub("\n", "", i) for i in f.readlines()]
except FileNotFoundError:
    print(f"文件 {input_path} 未找到，退出。")
    sys.exit(1)

print(f"User list for round {current_round}: {user_list}")


'''获取用户的微博资料'''
screen_names = []
for user_id in user_list:
    try:
        weibo_profile = get_weibo_profile(uid=user_id)
        screen_names.append("%40" + weibo_profile.screen_name)
    except Exception as e:
        print(f"获取用户 {user_id} 的资料时出错：{e}")
        continue

'''保存screen_names'''
output_path = f"step2_crawler/screen_names_{current_round}.txt"
with open(output_path, "w") as f:
    f.writelines("\n".join(screen_names))
output_path_spider = "step2_crawler/screen_names.txt" #覆盖保存，tweet_by_keyword需要，不想改爬虫文件了（（真的怕改错或者忘了
with open(output_path_spider, "w") as f:
    f.writelines("\n".join(screen_names))

print(f"Screen names for round {current_round}: {screen_names}") #该轮使用的screen_names



#weibo spider
'''使用Weibo Spider进行抓取'''
mode_to_spider = {
    'comment': CommentSpider,
    'fan': FanSpider,
    'follow': FollowerSpider,
    'user': UserSpider,
    'repost': RepostSpider,
    'tweet_by_tweet_id': TweetSpiderByTweetID,
    'tweet_by_user_id': TweetSpiderByUserID,
    'tweet_by_keyword': TweetSpiderByKeyword,
}
mode = 'tweet_by_keyword'
spider = mode_to_spider.get(mode)
process.crawl(spider)

'''输出爬取结果'''
process.start()



#new users @user_list
'''对tweet_by_keyword 从包含@本轮用户的tweet列表中保存新用户ID'''
path = "output_spider"
tweetlist = []

for file_name in os.listdir(path):
    try:
        if 'keyword' in file_name and user_list[0] in file_name and user_list[-1] in file_name:
            with open(os.path.join(path, file_name), "r", encoding = "UTF-8") as f:
                for line in f:
                    print(line)
                    tweetlist.append(json.loads(line))
    except FileNotFoundError as e:
        print(f"File not found. Error details: {e}")
        break
    
print(f"Total parsed tweets: {len(tweetlist)}")

mention_id_list = list(set([t["user"]["_id"] for t in tweetlist]))

'''检查重复项'''
def check_duplicate(mention_id_list, current_round):
    for r in range(1, current_round+1):
        past_path = f"step2_crawler/users_ids_{r}.txt"
        if os.path.exists(past_path):
            with open(past_path, "r") as f:
                user_list = [re.match("[0-9]*", re.sub("\n", "", i))[0] for i in f.readlines()]
            mention_id_list = set(mention_id_list) - set(user_list)

    return list(mention_id_list) #新用户ID

'''保存新用户ID至新一轮爬虫需要的users_ids.txt'''
new_user_list = check_duplicate(mention_id_list, current_round)
# save
output_path = f"step2_crawler/users_ids_{current_round+1}.txt"
with open(output_path, "w") as f:
    for item in new_user_list:
        f.write(item + "\n")
# spider
output_path_spider = "step2_crawler/users_ids.txt"
with open(output_path_spider, "w") as f:
    for item in new_user_list:
        f.write(item + "\n")


print(f"Round {current_round} completed. New user list saved to {output_path}")