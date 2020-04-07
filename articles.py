import configparser
from get.get import *
from db.conn import Sql
import json
import datetime
import re

cf = configparser.ConfigParser()
cf.read("conf/base_conf")


def get_expert_league_info(expert_id):
    url = cf.get("api", "expert_league_info")
    url = url.replace("@", str(expert_id))

    data = get_json_data(url)
    if not data:
        return
    data = data.get("data")
    for m in data:
        sql = Sql()
        expert_league = dict(table="expert_leaguematches")
        expert_league["expert_id"] = expert_id
        league_id = m.get("leagueMatchId")
        expert_league["leaguematch_id"] = league_id
        expert_league["leaguematch_name"] = m.get("leagueMatchName")
        expert_league["best_hitrate"] = m.get("bestMatchesHitRate")
        expert_league["hitrate_desc"] = m.get("totalHitRateDesc")
        if not sql.is_exists_by_tow(expert_league, "expert_id", "leaguematch_id"):
            sql.save(expert_league)
            print("save")
        sql.close()

        get_expert_league_articles(expert_id, league_id)


def get_expert_league_articles(expert_id, league_id):
    url = cf.get("api", "expert_league_articles")
    url = url.replace("expertid", str(expert_id)).replace("leagueid", str(league_id))
    data = get_json_data(url).get("data").get("threadList")
    print(json.dumps(data, ensure_ascii=False))
    for a in data:
        sql = Sql()
        print(json.dumps(a, ensure_ascii=False))
        article = dict(table="articles")
        article["id"] = a.get("threadId")
        article["title"] = a.get("threadTitle")
        article["expert_id"] = expert_id
        article["lottery_category_id"] = a.get("lotteryCategoryId")
        article["lottery_category_name"] = a.get("lotteryCategoryName")
        article["is_win"] = a.get("isWin")
        article["publish_time"] = a.get("publishTime")
        article["price"] = a.get("price")
        article["league_id"] = league_id

        for m in a.get("matchList"):
            match = dict(table="matches")
            match["category_id"] = m.get("categoryId")
            match["category_name"] = m.get("categoryName")
            match["info_id"] = m.get("matchInfoId")
            match["match_status"] = m.get("matchStatus")
            if match.get("match_status") == 3:
                match["status"] = "完"
            else:
                match["status"] = "未"
            match_time = m.get("matchTime")
            match_time = match_time.replace("/", "-").replace("/", "-")
            if not re.search("\d{4}", match_time):
                match_time = str(datetime.date.today().year) + "-" + match_time
            print(match_time)
            match["match_time"] = match_time

            league = dict(table="leaguematch")
            league_id = m.get("leagueId")
            league_name = m.get("leagueName")
            league["id"] = league_id
            league["name"] = league_name
            sql.save_if_not_exist(league)

            match["league_id"] = league_id
            match["league_name"] = league_name
            match["guest_name"] = m.get("guestName")
            match["guest_score"] = m.get("guestScore")
            match["home_name"] = m.get("homeName")
            match["home_score"] = m.get("homeScore")
            sql.save_if_not_exist(match, "info_id")

            article_match = dict(table="article_match")
            article_match["article_id"] = article["id"]
            article_match["info_id"] = match["info_id"]
            if not sql.is_exists_by_tow(article_match, "article_id", "info_id"):
                sql.save(article_match)

        ret = sql.save_if_not_exist(article)
        if ret == 0:
            article["table"] = "articles"
            sql.update(article, "league_id")

        sql.close()

def get_article_detail(article_id):
    sql = Sql()
    url = cf.get("api", "expert_article_detail")
    url = url.replace("@", str(article_id))
    data = get_json_data(url).get("data")
    article_detail = dict(table="article_details")
    article_detail["id"] = article_id
    article_detail["content"] = data.get("content")
    sql.save_if_not_exist(article_detail)
    sql.close()


def start_articles():
    print("start")
    sql = Sql()
    ret, err = sql.execute("select id from expert")
    if err != 0:
        return
    ret = [i[0] for i in ret]
    for id in ret:
        get_expert_league_info(id)


def start_article_details():
    sql = Sql()
    ret, err = sql.execute("select id from articles")
    for r in ret:
        get_article_detail(r[0])


if __name__ == '__main__':
    start_articles()
    start_article_details()

