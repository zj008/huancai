import requests
import logging


class StatusCodeError(Exception):
    def __str__(self):
        return "status code error"


def get_json_data(url):
    ret = requests.get(url)
    if ret.status_code != 200:
        logging.error("status code err while get " + url)
        return
    res = ret.json()
    return res


def get_source_data(url):
    ret = requests.get(url)
    if ret.status_code != 200:
        logging.error("status code err while get " + url)
        return
    return ret.text