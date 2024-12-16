import re
import os

os.chdir("/Users/pootaatoos/Desktop/研究/LGBT_network") #Change to your path

with open("step2_crawler/users_ids.txt","r") as f:
    mention_id_list=[re.sub("\n","",i) for i in f.readlines()]


def check_duplicate(mention_id_list, round):
    for r in range(1, round):
        path = "step2_crawler/users_ids_" + str(r) + ".txt"
        with open(path,"r") as f:
            user_list=[re.match("[0-9]*", re.sub("\n","",i))[0] for i in f.readlines()]
        mention_id_list = set(mention_id_list) - set(user_list)

    return list(mention_id_list)

print(len(mention_id_list))
