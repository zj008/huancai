from lxml import etree
import datetime
from db.conn import Sql
import json
from get.get import get_content_data
import configparser
import re
import os


cf = configparser.ConfigParser()
cf.read("conf/base_conf")


def parse_expert(info, cla):
    """
    :param info:  专家信息
    :param cla:  0：足球专家   1：篮球专家
    """
    sql = Sql()
    expert = dict(table="expert")
    expert["avg_odds"] = info.get("avgOdds")  # 平均赔率
    expert["ball_rate"] = info.get("bAllRate")  # 最近预测结果
    expert["earning_rate"] = info.get("earningRate", 0)  # 盈利率
    expert["hit_rate"] = info.get("hitRate", 0)
    expert["max_win"] = info.get("maxWin")
    expert["nickname"] = info.get("nickname")  # 昵称
    expert["show_hit_rate"] = info.get("showHitRate")  # ？？？
    expert["slogan"] = info.get("slogan")  # 职业
    expert["trend"] = info.get("trend")  # ？？？
    expert["id"] = info.get("userId")  # 用户id
    expert["weight"] = info.get("weight")  # 体重
    field = "foot" if cla == 0 else "basket"  # 判断是足球专家还是篮球专家
    expert[field] = 1
    avatar_url = info.get("avatar")
    expert["avatar"] = str(expert.get("id")) + "." + avatar_url.split(".")[-1]
    ret = sql.save_if_not_exist(expert)

    if ret == 0:
        expert["table"] = "expert"
        sql.update(item=expert, field=field)
    else:
        avatar_path = cf.get("path", "avatar")
        avatar_url = info.get("avatar")  # 头像
        content = get_content_data(avatar_url)
        if content:
            save_pic(str(avatar_path + str(expert.get("id"))) +".jpg", content)

    leagueMatchs = info.get("leagueMatchStats")  # 该专家擅长的联赛信息列表
    for s in leagueMatchs:
        league_match = dict(table="leaguematch")
        league_match["id"] = s.get("leagueMatchId")
        league_match["name"] = s.get("leagueMatchName")
        sql.save_if_not_exist(league_match)

        expert_leaguematch = dict(table="expert_leaguematch")
        expert_leaguematch["expert_id"] = expert.get("id")
        expert_leaguematch["leaguematch_id"] = s.get("leagueMatchId")
        sql.save(expert_leaguematch)
    sql.close()


def parse_hot_expert(data, status, index):
    expert = dict(table="hot_expert")
    expert["id"] = data.get("userId")
    expert["popularity"] = data.get("popularity")
    expert["earning_rate"] = data.get("earningRate")
    expert["type"] = status
    expert["top_index"] = index
    sql = Sql()
    sql.save(expert)


def parse_expert_articles(data, expert_id):

    sql = Sql()

    match_info = data.get("earliestMatch")

    article = dict(table="articles")
    article["info_id"] = match_info.get("matchInfoId")
    article["guest_name"] = match_info.get("guestName")
    article["home_name"] = match_info.get("homeName")
    article["guest_score"] = match_info.get("guestScore")
    article["home_score"] = match_info.get("homeScore")
    article["league_id"] = match_info.get("leagueId")
    article["league_name"] = match_info.get("leagueName")
    article["match_status"] = match_info.get("matchStatus")
    article["match_time"] = match_info.get("matchTime")
    article["guest_score"] = match_info.get("guestScore")
    article["id"] = data.get("threadId")
    article["expert_id"] = expert_id
    article["is_win"] = data.get("isWin")
    article["lottery_category_id"] = data.get("lotteryCategoryId")
    article["lottery_category_name"] = data.get("lotteryCategoryName")
    article["price"] = data.get("price")
    article["publish_time"] = data.get("publishTime")
    article["title"] = data.get("title")
    ret = sql.save_if_not_exist(article)
    return ret, article.get("id")


def parse_football_match(data):
    sql = Sql()

    l = data.get("leagueMatch")
    league_match = dict(table="leaguematch")
    league_match["id"] = l.get("leagueId")
    league_match["name"] = l.get("leagueName")
    sql.save_if_not_exist(league_match)


    g1 = data.get("guestTeam")
    parse_team(g1)

    g2 = data.get("homeTeam")
    parse_team(g2)

    match = dict(table="matches")
    d = data.get("footballLiveScore")
    match["match_id"] = d.get("matchId")
    match["info_id"] = d.get("matchInfoId")
    match["match_status"] = d.get("matchStatus")
    match["status"] = d.get("status")
    match["card_highlight"] = d.get("cardHighlight")
    match["corner_kick"] = d.get("cornerKick")
    match["guest_red_card"] = d.get("guestRedCard")
    match["guest_score"] = d.get("guestScore")
    match["guest_yellow_card"] = d.get("guestYellowCard")
    match["half_score"] = d.get("halfScore")
    match["home_red_card"] = d.get("homeRedCard")
    match["home_score"] = d.get("homeScore")
    match["home_yellow_card"] = d.get("homeYellowCard")
    match["guest_id"] = g1.get("teamId")
    match["home_id"] = g2.get("teamId")
    match["league_id"] = l.get("leagueId")
    match["league_name"] = l.get("leagueName")
    match["match_type"] = 0
    match_time = data.get("matchTime")
    if match_time:
        match_time *= pow(10, -3)
        match["match_time"] = datetime.datetime.fromtimestamp(match_time)

    sql.reset_if_exist(match, "info_id")
    sql.close()


def parse_basketball_match(data):
    sql = Sql()

    l = data.get("leagueMatch")
    league_match = dict(table="leaguematch")
    league_match["id"] = l.get("leagueId")
    league_match["name"] = l.get("leagueName")
    sql.save_if_not_exist(league_match)

    g1 = data.get("guestTeam")
    parse_team(g1)

    g2 = data.get("homeTeam")
    parse_team(g2)

    match = dict(table="matches")
    m = data.get("basketballLiveScore")
    match["guest_score"] = m.get("guestScore")
    match["home_score"] = m.get("homeScore")
    match["match_id"] = m.get("matchId")
    match["info_id"] = m.get("matchInfoId")
    match["match_status"] = m.get("matchStatus")
    match["status"] = m.get("status")
    match["guest_id"] = g1.get("teamId")
    match["home_id"] = g2.get("teamId")
    match["match_type"] = 1
    match_time = data.get("matchTime")
    if match_time:
        match_time *= pow(10, -3)
        match["match_time"] = datetime.datetime.fromtimestamp(match_time)
    match["league_id"] = l.get("leagueId")
    match["league_name"] = l.get("leagueName")
    sql.reset_if_exist(match, "info_id")
    sql.close()


def parse_news(data):
    news = dict(table="news")
    ct = data.get("createTime")
    if ct:
        news["create_time"] = datetime.datetime.fromtimestamp(ct * pow(10, -3))
    # news["imgsrc"] = data.get("imgsrc")
    news["source"] = data.get("source")
    news["title"] = data.get("title")
    news["url"] = data.get("url")
    news["docid"] = data.get("docid")
    return news


def prser_news_content(news, data):
    docid = news.get("docid")
    if data:
        data = data.get(docid)
    else:
        return
    body = data.get("body")

    sql = Sql()
    ret = sql.is_exists(news, "docid")
    if ret == 0:
        # 去除视频标签
        body = re.sub("\<!--VIDEO#\d+\-\-\>", "", body)
        body = re.sub("<p>\s+<b>【欢迎搜索关注公众号“足球大会”.*", "", body)
        # 将图片标签替换成静态图片
        for i, img in enumerate(data.get("img"), 0):
            src = img.get("src")
            digit = hash(data.get("docid"))
            _, s = divmod(digit, 26)
            dir = chr(s + 97)
            base = cf.get("path", "news")
            path = os.path.join(base, dir, docid+f"_{i}."+ src.split(".")[-1])
            img_path = path.replace("./static", "")
            body = body.replace(img.get("ref"), f'<img src="{img_path}">')
            img_content = get_content_data(img.get("src"))
            save_pic(path, img_content)
        news["content"] = body
        sql.save(news)
    sql.close()


def parse_team(data):
    sql = Sql()
    team = dict(table="team")
    team["team_type"] = 0
    id = data.get("teamId")
    team["id"] = id
    team["full_name"] = data.get("fullName")
    icon_url = data.get("teamIcon")
    icon_name = ""
    if icon_url:
        icon_type = icon_url.split(".")[-1]
        icon_name = f"{id}.{icon_type}"
        team["icon"] = icon_name
    team["name"] = data.get("teamName")
    ret = sql.save_if_not_exist(team)
    if ret == 1 and icon_name:
        content = get_content_data(icon_url)
        base_path = cf.get("path", "team")
        icon_path = os.path.join(base_path, icon_name)
        save_pic(icon_path, content)
    sql.close()

def save_pic(path, content):
    with open(path, "wb") as f:
        f.write(content)
