import os
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
from openai import OpenAI
import pandas as pd

china_provinces = [
    "北京", "天津", "上海", "重庆",  # 直辖市
    "河北", "山西", "辽宁", "吉林", "黑龙江",  # 华北、东北
    "江苏", "浙江", "安徽", "福建", "江西", "山东",  # 华东
    "河南", "湖北", "湖南", "广东", "海南",  # 华中、华南
    "四川", "贵州", "云南", "陕西", "甘肃", "青海",  # 西南、西北
    "内蒙古", "广西", "西藏", "宁夏", "新疆",  # 自治区
    "香港", "澳门", "台湾"  # 特别行政区和台湾省
]

client = OpenAI(
    api_key="sk-5e40de76096044dfbc27b37f9ca0f436",
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

    
def user_check(screen_name, description, verify_information, gpt = None):
    """
    Checks if a Weibo account is an official account based on 
    its screen name, description, and verification information.
    The function uses a combination of keyword matching in the 
    screen name and description, province name matching, and 
    verification level to determine if the account is official. 
    It also utilizes an external AI model to assist in the 
    classification.
    
    Args:
        screen_name (str): The screen name of the Weibo account.
        description (str): The description of the Weibo account.
        verify_information (int): The verification level of the Weibo account.
        gpt (bool|None): determining whether use gpt or not
    Returns:
        bool: True if the account is determined to be official, False otherwise.
    
    """
    province = any(word in china_provinces for word in screen_name)
    verified = verify_information >= 1

    if gpt:
        completion = client.chat.completions.create(
            model="qwen2.5-3b-instruct",
            messages=[
                {'role': 'system', 'content': 'You are a helpful classifier for whether an weibo account is official account, based on its screen name and description.'},
                {'role': 'user', 'content': f'请根据昵称“{screen_name}”与其个人简介“{description}，判断该账号是否为官方账号。是的话，请返回“True”，不是的话，请返回“False”'}],
        )
        
        result_dict = json.loads(completion.model_dump_json())
        result = "True" in result_dict["choices"][0]["message"]["content"]
    else:
        result = False

    return result or (province and verified)


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
user_data = pd.read_csv("step2_crawler/weibo/users.csv")

try:
    with open(input_path, "r") as f:
        user_list = []
        screen_names = []
        user_list_original = [re.sub("\n", "", i) for i in f.readlines()]
        information_user = [user_data[user_data["用户id"] == id] for id in user_list_original]
        information_list = [(info["用户id"].values[0], info["昵称"].values[0], info["简介"].values[0], info["认证类型"].values[0]) for info in information_user]

        for id, *information in information_list:
            if not user_check(*information, gpt = False):
                user_list.append(id)
                screen_names.append(information[0])

except FileNotFoundError:
    print(f"文件 {input_path} 未找到，退出。")
    sys.exit(1)

print(f"User list for round {current_round}: {user_list}")

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