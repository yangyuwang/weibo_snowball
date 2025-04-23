
import pandas as pd
from subprocess import run
import json
import os

#mongo_db_link = "mongodb://localhost:27017/"
base_dir = os.path.dirname(os.path.abspath(__file__)) #先改成本地路径并且保存微博到csv了（（（在36行
os.chdir(base_dir)
cookie = "_T_WM=718f99622b94d66f4649e5cb0a3d43ae; MLOGIN=1; M_WEIBOCN_PARAMS=oid%3D5154731124331829%26luicode%3D10000011%26lfid%3D1076032389651505; SCF=AsV2nMyc49QaHAW-FEEaN8vQW1putmQFzzvvJvsqbVjlGtehxikuhQWmia_aok0_fzeFvcyJFZv5NGz48haZ5sQ.; SUB=_2A25FBcRXDeRhGedH6VsZ9yjKwzuIHXVme1mfrDV6PUJbktANLRTHkW1NUNJPOoTaXk1JLTftuxqJrE_yDzEmlrP7; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWHYRT.TV11w4jiSdK_jqgg5NHD95Qp1Kz41hMcSonNWs4DqcjZxGUyMJ9k-NxyMntt; SSOLoginState=1744942088; ALF=1747534088"

# id
df = pd.read_excel("User.xlsx")
user_id = df[df['gender'] == "m"]["id"].tolist()

# keywords
keywords = ["对象", "男朋友", "老公", "npy", "前任", "前夫", "前男友"]
keywords_str = " ".join(keywords)

# file path
file_relative_path = "Picture"   #在step2_crawler/weibo/爬取的user的id/“这里创建一个名为123的文件夹，图片存在这里面”
#如果要放在step2_crawler外面或者随便怎么改都ok，但是要在weibo.py里面改路径
# 在weibo.py里：
# 1）655行，这里好像可以把图片保存路径暴力改成主路径下的随便哪个地方，目前我改成了file_dir+file_relative_path
# 2）1304-1328行，这里是在step2_crawler下创建了file_dir = weibo/爬取的user的id并且存里面，可以改file_dir
# 1304-1328行中还会给img和video自动创建两个文件夹，我给取消了

# config
def modify_config(config_path):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)
frevrfev re
    # 修改配置项
    config["user_id_list"] = user_id[573:581]
    #config["user_id_list"] = f"users_ids_{current_round}_left.txt"  # 每轮次的用户列表文件（此处为断点续爬）
    config["write_mode"] = ["csv"] #["mongo"]
    config["only_crawl_original"] = 0  # 是否只抓取原创微博
    config["remove_html_tag"] = 1  # 是否移除HTML标签
    config["since_date"] = "2009-01-01"  # 爬取的起始日期/距今日期
    config["start_page"] = 1
    config["original_pic_download"] = 1  # 是否下载原创微博中的图片
    config["retweet_pic_download"] = 0  # 是否下载转发微博中的图片
    config["original_video_download"] = 0  # 是否下载原创微博中的视频
    config["retweet_video_download"] = 0  # 是否下载转发微博中的视频
    config["download_comment"] = 0  # 是否下载评论
    config["comment_max_download_count"] = 1000  # 最大评论下载数
    config["download_repost"] = 0  # 是否下载转发
    config["repost_max_download_count"] = 1000  # 最大转发下载数
    config["cookie"] = cookie
    #config["mongodb_URI"] = mongo_db_link #mongodb link

    # 保存修改后的配置文件
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)

config_path = "step2_crawler/config.json"

# 爬取微博文本和关键词图片
modify_config(config_path)
run(['python', 'step2_crawler/weibo.py', keywords_str, file_relative_path])
