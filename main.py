from get.get import *
from parse.parse import *
import configparser
from db.conn import Sql
import datetime
import threading
from threading import Timer


cf = configparser.ConfigParser()
cf.read("conf/base_conf")


def get_expert(cla):
    """
    获取所有专家信息
    :param url: 请输入获取所有足球专家的url或者获取所有篮球专家的url
    :param cla: 0： 足球专家， 1： 篮球专家
    """
    if cla == 0:
        url = cf.get("api", "football_expert_url")
    elif cla == 1:
        url = cf.get("api", "basket_expert_url")
    else:
        return
    expert_list = get_json_data(url).get("data").get("expertList")
    for e in expert_list:
        parse_expert(e, cla=0)


def get_hot_expert(status):
    """
    获取人气榜和盈利棒专家信息
    :param url: 盈利榜或者人气榜的链接
    :param status: 0： 盈利榜， 1：人气榜
    """
    if status == 1:
        url = cf.get("api", "football_renqi_url")
    elif status == 0:
        url = cf.get("api", "football_earning_url")
    else:
        return
    data = get_json_data(url).get("data")
    for index, info in enumerate(data, 1):
        # print(info)
        parse_hot_expert(info, status, index)


def get_articles():
    sql = Sql()
    ret, err = sql.execute("select id from expert")
    expert_ids = []
    if err == 0:
        expert_ids = [id[0] for id in ret]
    for id in expert_ids:
        get_expert_articles(id)


def get_expert_articles(expert_id):
    url = cf.get("api", "expert_articles_url")
    url = url.replace("userid", str(expert_id))
    try:
        out_sale_data = get_json_data(url).get("data").get("outSalePlanList")
    except AttributeError as e:
        print(e)
        return
    for data in out_sale_data:
        ret, article_id = parse_expert_articles(data, expert_id)
        if ret != 0:
            get_articles_detail(article_id)


def get_articles_detail(article_id):
    article_detail = dict(table="article_details")
    article_detail["id"] = article_id
    detail_url = cf.get("api", "article_detail_url")
    detail_url = detail_url.replace("articleid", str(article_id))
    data = get_json_data(detail_url).get("data")
    content = data.get("content")
    article_detail["content"] = content
    sql = Sql()
    sql.save_if_not_exist(article_detail)
    sql.close()


def get_matchs(date, match_type):
    date = date.strftime("%Y-%m-%d")
    url = ""
    if match_type == 0:
        url = cf.get("api", "football_match_url")
    elif match_type == 1:
        url = cf.get("api", "basketball_match_url")
    if not url:
        return
    url = url.replace("@", "%").replace("date", date)
    data = get_json_data(url).get("data")
    print(date, len(data))
    if match_type == 0:
        for d in data:
            parse_football_match(d)
    elif match_type == 1:
        for d in data:
            parse_basketball_match(d)


def get_news(news_type=0, limit=None):
    """
    :param news_type: 0->获取足球新闻， 1->获取篮球新闻
    :param limit:  默认获取前20条
    """
    if limit == None or type(limit) != int:
        limit = 20
    url = ""
    if news_type == 0:
        url = cf.get("api", "foot_news")
    elif news_type == 1:
        url = cf.get("api", "basket_news")
    if not url:
        return
    url = url + str(limit)
    data = get_json_data(url).get("data")
    for d in data:
        news = parse_news(d)
        news["news_type"] = news_type
        get_news_content(news)


def get_news_content(news):
    docid = news.get("docid")
    url = f"https://hongcai.163.com/api/ext/newsFull/{docid}.json"
    print(url)
    data = get_json_data(url)
    if data:
        data = data.get(docid)
    else:
        return
    content = data.get("body")
    news["content"] = content
    for index, img in enumerate(data.get("img"), 0):
        news["img" + str(index)] = img.get("src")
        if index >= 10:
            break
    sql = Sql()
    sql.save_if_not_exist(news, "docid")
    sql.close()

def run():
    # 获取足球专家
    get_expert(0)
    # 获取篮球专家
    get_expert(1)
    # 获取所有专家文章
    get_articles()

    # 获取专家排行榜
    sql = Sql()
    try:
        sql.execute("truncate table hot_expert")
        sql.db.commit()
    except Exception as e:
        print(e)
    sql.close()
    get_hot_expert(0)
    get_hot_expert(1)

    today = datetime.date.today()
    delter = datetime.timedelta(days=1)
    yesterday = today - delter
    tomorrow = today + delter
    after_tomorrow = tomorrow + delter
    # 获取足球比赛信息
    get_matchs(yesterday, 0)
    get_matchs(today, 0)
    get_matchs(tomorrow, 0)
    get_matchs(after_tomorrow, 0)

    # 获取篮球比赛信息
    get_matchs(yesterday, 1)
    get_matchs(today, 1)
    get_matchs(tomorrow, 1)
    get_matchs(after_tomorrow, 1)

    # 获取新闻资讯
    get_news(0)
    get_news(1)
    t = Timer(3600*24, run)
    with open("log.file", "w") as f:
        f.write(datetime.datetime.now().strftime("%Y-m%-%d %X"))


if __name__ == '__main__':
    run()


