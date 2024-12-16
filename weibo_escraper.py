# -*- coding:utf-8 -*-

"""
 Author: helixcs
 Site: https://iliangqunru.bitcron.com/
 File: weibo_scraper.py
 Time: 3/16/18
 
 Revision by Huang Ronggui
 Time: 15//3/19
"""

import datetime
import sys
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator, Optional
from weibo_base import exist_get_uid, \
    get_tweet_containerid, weibo_tweets, weibo_getIndex, UserMeta, WeiboTweetParser, WeiboGetIndexParser

try:
    assert sys.version_info.major == 3
    assert sys.version_info.minor >= 6
except AssertionError:
    raise RuntimeError('weibo-scrapy requires Python3.6+ !')

now = datetime.datetime.now()
CURRENT_TIME = now.strftime('%Y-%m-%d %H:%M:%S')
CURRENT_YEAR = now.strftime('%Y')
CURRENT_YEAR_WITH_DATE = now.strftime('%Y-%m-%d')
pool = ThreadPoolExecutor(100)

_TweetsResponse = Optional[Iterator[dict]]
_UserMetaResponse = Optional[UserMeta]


class WeiBoScraperException(Exception):
    def __init__(self, message):
        self.message = message


def get_weibo_tweets_by_name(name: str, pages: int = None, start_at: int = 1) -> _TweetsResponse:
    """
    Get weibo tweets by nick name without any authorization
    >>> from weibo_scraper import  get_weibo_tweets_by_name
    >>> for tweet in get_weibo_tweets_by_name(name='嘻红豆', pages=1):
    >>>     print(tweet)
    :param name: nick name which you want to search
    :param pages: pages, default all pages
    :return: _TweetsResponse
    """
    if name == '':
        raise WeiBoScraperException("name from <get_weibo_tweets_by_name> can not be blank!")
    _egu_res = exist_get_uid(name=name)
    exist = _egu_res.get("exist")
    uid = _egu_res.get("uid")
    if exist:
        inner_tweet_containerid = get_tweet_containerid(uid=uid)
        yield from get_weibo_tweets(tweet_container_id=inner_tweet_containerid, pages=pages, start_at=start_at)
    else:
        yield None


def get_weibo_tweets_by_uid(uid: int, pages: int = None) -> _TweetsResponse:
    """
    Get weibo tweets by uid without any authorization
    >>> from weibo_scraper import  get_weibo_tweets_by_name
    >>> for tweet in get_weibo_tweets_by_uid(uid=3637346297, pages=1):
    >>>     print(tweet)
    :param uid: uid which you want to search
    :param pages: pages ,default all pages
    :return: _TweetsResponse
    """
    if uid == '':
        raise WeiBoScraperException("name from <get_weibo_tweets_by_name> can not be blank!")
    if weibo_getIndex(uid).get("ok"):
        inner_tweet_containerid = get_tweet_containerid(uid=uid)
        yield from get_weibo_tweets(tweet_container_id=inner_tweet_containerid, pages=pages)
    else:
        yield None


def get_weibo_tweets(tweet_container_id: str, pages: int = None, start_at: int=1) -> _TweetsResponse:
    """
    Get weibo tweets from mobile without authorization,and this containerid exist in the api of

    Compatibility:
    New Api
    1. Search by Nname and get uid by this api "https://m.weibo.cn/api/container/getIndex?queryVal=来去之间&containerid=100103type%3D3%26q%3D来去之间"
    2. Get profile info by uid , https://m.weibo.cn/api/container/getIndex?type=uid&value=1111681197
    3. https://m.weibo.cn/api/container/getIndex?containerid=2302831111681197
    3. Get weibo tweets by container in node of "tabs" ,https://m.weibo.cn/api/container/getIndex?containerid=2304131111681197_-_&page=6891
    >>> from weibo_scraper import  get_weibo_tweets
    >>> for tweet in get_weibo_tweets(tweet_container_id='1076033637346297',pages=1):
    >>>     print(tweet)
    >>> ....
    :param tweet_container_id:  request weibo tweets directly by tweet_container_id
    :param pages :default None
    :return _TweetsResponse
    """

    def gen(_inner_current_page=start_at):
        attempt = 1 ## the loop will break after N unsuccessful attempts. 
        while True:
            if pages is not None and _inner_current_page > pages:
                print('Last_Page in this Loop:',_inner_current_page-1)
                break
            _response_json = weibo_tweets(containerid=tweet_container_id, page=_inner_current_page)
            if _response_json is None:
                print("skip bad request")
                continue
            elif _response_json.get("ok") != 1: ## 此情况为此页没有微博（删除 | 隐藏）
                print("{}: failed response at page {}".format(attempt, _inner_current_page))
                if attempt <= 20: ## Change the Attempt Number
                    _inner_current_page += 1
                    attempt += 1
                    continue
                else:
                    print("break failed response after {} attemps".format(attempt))
                    break
            elif _response_json.get('data').get("cards")[0].get('name') == '暂无微博':
                print("{}: potential end tweet at page {}".format(attempt, _inner_current_page))
                if attempt <= 20: ## Change the Attempt Number
                    _inner_current_page += 1
                    attempt += 1
                    continue
                else:
                    print("break potential end tweet after {} attemps".format(attempt))
                    break
            _cards = _response_json.get('data').get("cards")
            attempt = 1  # reset if the next attemp is sucessful
            for _card in _cards:
                # skip recommended tweets
                if _card.get("card_group"):
                    continue
                # just yield field of mblog
                yield _card
            _inner_current_page += 1

    yield from gen()

def get_weibo_profile(name: str = None, uid: str = None) -> _UserMetaResponse:
    """
    Get weibo profile
    >>> from weibo_scraper import get_weibo_profile
    >>> weibo_profile = get_weibo_profile(name='嘻红豆',)
    >>> ...weibo_profile
    :param uid: uid
    :param name: name
    :return: UserMeta
    """
    if uid is not None:
        _uid = uid
    elif name is not None:
        _egu_response = exist_get_uid(name=name)
        if not _egu_response.get('exist'):
            return None
        _uid = _egu_response.get('uid')
    else:
        return None
    _weibo_get_index_response_parser = WeiboGetIndexParser(get_index_api_response=weibo_getIndex(uid_value=_uid))
    if _weibo_get_index_response_parser.raw_response is None \
            or _weibo_get_index_response_parser.raw_response.get('data') == 0:
        return None
    return _weibo_get_index_response_parser.user