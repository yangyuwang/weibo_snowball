# Weibo Snowball Sampling

weibo crawler (tweets & user information) -> weibo spider (mentioning tweets)

## Crawler in step2_crawler/weibo.py

This step scrapes down the tweets in folder `weibo`, and also user information in `users.csv`.

(`users.csv` would be used in spider)

## Spider in minor_scrape.py

This step utilizes the getting tweets by keywords function to get tweets mentioning current round users ("@screen_name").

To prevent the official accounts (such as government, groups...) influence the snowballing process, we detect the account type by its screen name, verification information, and description:

1. if screen name contains province name, and the verification information is not personal, then the account would be considered as official account.

2. (when setting to use gpt,) a large language model would be used based on the screen name and descriptions to determine whether it is a official account or not. (The information of the model see here: [qwen2.5-3b-instruct](https://huggingface.co/Qwen/Qwen2.5-3B-Instruct))

## face detection by opencv (tbd)