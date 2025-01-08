import subprocess
import json

'''轮次'''
max_rounds = 1
since_date = "2015-01-01"
seed_user_list = ["5660911274"]
mongo_db_link = "mongodb+srv://wangyd:Yangyu20010105@cluster0.vhukb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
cookie = "SCF=AgkTH1YYXZOLwOaBjfWUm2p6b9_PjPnTUtbA-Hm5Ow55F6GuWeaJKvEZsfytDQ8E5ml8fIElFC3HbKzTkrHsQ34.; SINAGLOBAL=1561705964949.92.1734351993621; XSRF-TOKEN=RgsPhdOpspxWIXi1Ob1a-eAR; _s_tentry=weibo.com; Apache=1875282394395.8318.1735555998197; ULV=1735555998201:4:4:1:1875282394395.8318.1735555998197:1734364351051; SUB=_2A25KdgzWDeRhGeFJ6VUT-CbIyzSIHXVpCgAerDV8PUNbmtANLVPbkW9NfEW7UXPslOlfZAigatKcDcWUAQmCIK3K; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFpTlIcKMPL1Yom5_JrAsml5JpX5KzhUgL.FoMNeoME1hnXehn2dJLoIfQLxK-LB.-L1KMLxK-L122LB-2LxK-L122L1-zLxKqLBozLBK2LxKqLBoeL1K-LxK-L1hML1hqLxKML1hzLBo.LxKBLBonL12zLxKML12qLB-BLxKBLB.2L1hqt; ALF=02_1738148230; WBPSESS=Dt2hbAUaXfkVprjyrAZT_J64aYFgeacWa7JYF7sASGcZ49gGC4zbi686UzSiZOcdERwHdQCOzEC1-3W4z22TswE3a7-IY3lHrdI1IuafduqTTWsCgj8QEcfuhIMZpcCJXOeI8irzJ2aTo8ZVy_Q4zn7bK5Kz7d7pGG4RaRmcUV18ysMiVvfxyhEIzh0bbz78d_oKTTAsHsNc0uFIgUFgWg=="

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
    config["since_date"] = since_date  # 爬取的起始日期/距今日期
    config["original_pic_download"] = 1  # 是否下载原创微博中的图片
    config["retweet_pic_download"] = 0  # 是否下载转发微博中的图片
    config["original_video_download"] = 0  # 是否下载原创微博中的视频
    config["retweet_video_download"] = 0  # 是否下载转发微博中的视频
    config["download_comment"] = 0  # 是否下载评论
    config["comment_max_download_count"] = 1000  # 最大评论下载数
    config["download_repost"] = 0  # 是否下载转发
    config["repost_max_download_count"] = 1000  # 最大转发下载数
    config["cookie"] = cookie
    config["mongodb_URI"] = mongo_db_link #mongodb link

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
