import subprocess
import json

'''轮次'''
max_rounds = 2
since_date = "2015-01-01"
seed_user_list = ["5660911274"]

'''第一轮要爬的ids'''
users_ids_round1 = seed_user_list #第一轮要爬的ids
with open("step2_crawler/users_ids.txt", "w") as f: #覆盖成要爬的第一轮的users_ids
    for i in users_ids_round1:
        f.write(i + "\n")
with open("step2_crawler/users_ids_1.txt", "w") as f: #覆盖成要爬的第一轮的users_ids
    for i in users_ids_round1:
        f.write(i + "\n")


'''修改配置文件'''
# 配置文件路径
config_path = "step2_crawler/config.json"

# 函数：修改配置文件
def modify_config(config_path, current_round):
    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    # 修改配置项
    config["user_id_list"] = f"users_ids_{current_round}.txt"  # 每轮次的用户列表文件
    config["write_mode"] = ["mongo"]
    config["only_crawl_original"] = 0  # 是否只抓取原创微博
    config["remove_html_tag"] = 1  # 是否移除HTML标签
    config["since_date"] = 5  # 爬取的起始日期/距今日期
    config["original_pic_download"] = 1  # 是否下载原创微博中的图片
    config["retweet_pic_download"] = 0  # 是否下载转发微博中的图片
    config["original_video_download"] = 0  # 是否下载原创微博中的视频
    config["retweet_video_download"] = 0  # 是否下载转发微博中的视频
    config["download_comment"] = 0  # 是否下载评论
    config["comment_max_download_count"] = 1000  # 最大评论下载数
    config["download_repost"] = 0  # 是否下载转发
    config["repost_max_download_count"] = 1000  # 最大转发下载数
    config["cookie"] = "SCF=Ar11oB-yEgjxtlMBhJMTYH1t2nl2EA-YxmTVMALrygV8F36YgK1ZMgyHDzqXyTiPCkxgRIrICaz8BEmynvFP3VA.; ALF=1736881030; _T_WM=83921483250; XSRF-TOKEN=c123d2; WEIBOCN_FROM=1110006030; SUB=_2A25KW1bWDeRhGeNK7VsZ-S7Iwj2IHXVpGdYerDV6PUJbktAYLVetkW1NSTq1lyIMmY_s3FWqKUKqAT40WHleWUuV; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9W5ZaDes33M59QOyQZ1_SEKF5JpX5KMhUgL.Fo-XSo.R1K5X1K22dJLoIpBLxKqLBoBL12zLxKnL122L12i7d7tt; SSOLoginState=1734289030; MLOGIN=1; M_WEIBOCN_PARAMS=uicode%3D20000061%26fid%3D5111959639560755%26oid%3D5111959639560755"
    config["mongodb_URI"] = "mongodb+srv://wangyd:Yangyu20010105@cluster0.vhukb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

    # 保存修改后的配置文件
    with open(config_path, 'w') as config_file:
        json.dump(config, config_file, indent=4)



if __name__ == "__main__":
    current_round = 1

    while current_round <= max_rounds:
        print(f"开始第 {current_round} 轮爬取")
        #修改配置文件为本轮爬取的需求
        modify_config(config_path, current_round)
        #调用crawler，爬当前轮次用户微博
        subprocess.run(['python', 'step2_crawler/weibo.py'])
        #调用minor_scrape.py，传递当前轮次参数，爬mention，生成新一轮用户
        subprocess.run(['python', 'minor_scrape.py', str(current_round)])

        current_round += 1
