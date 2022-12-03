import datetime as dt
import os

import requests
from django.utils.timezone import make_aware

from .models import Base, Comment, Job, Poll, PollOption, Story

news_base_detail_url = "https://hacker-news.firebaseio.com/v0/item/"
top_news_link = "https://hacker-news.firebaseio.com/v0/topstories.json"
job_news_link = "https://hacker-news.firebaseio.com/v0/jobstories.json"


def fetch_news(url):
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()


def populate_fields(news_detail):
    type = news_detail.get("type")
    obj_id = str(news_detail.get("id"))
    by = news_detail.get("by")
    kids = list(reversed(sorted(news_detail.get("kids", []))))
    parent = news_detail.get("parent")
    secs = news_detail.get("time")
    title = news_detail.get("title")
    text = news_detail.get("text")
    time = make_aware(dt.datetime.fromtimestamp(secs))
    url = news_detail.get("url")
    score = news_detail.get("score", 0)
    parts = news_detail.get("parts", [])
    vals = {
        "type": type,
        "obj_id": obj_id,
        "by": by,
        "time": time,
        "url": url,
        "title": title,
        "text": text,
        "score": score,
        "generated": True,
    }
    return vals, (kids, parent, parts)


def get_children(type, kids, par, obj, grandchild=False):
    if not kids:
        return

    for comment_id in kids:
        print(
            f"{obj._meta.model_name} parent_id",
            par.id,
            "child",
            comment_id,
            end="...",
        )
        comment = fetch_news(f"{news_base_detail_url}{comment_id}.json")
        results = populate_fields(comment)
        actual_comment = results[0]
        story_type = actual_comment["type"]
        kidds = results[-1][0]
        if type == "story":
            s_par = obj.objects.create(**actual_comment, story_id=par.id)
        else:
            s_par = obj.objects.create(**actual_comment, poll_id=par.id)
        get_children(story_type, kidds, s_par, obj, grandchild=True)


def populate_database(news_ids, num=100):
    news_ids = list(reversed(sorted(news_ids)))[:num]
    if news_ids:
        exists = Base.objects.filter(obj_id=news_ids[0]).exists()
        if exists:
            return
    else:
        return
    news_dict = {
        "job": Job,
        "poll": Poll,
        "story": Story,
    }
    for news in news_ids:
        news_detail = fetch_news(f"{news_base_detail_url}{news}.json")
        ite = populate_fields(news_detail)
        news_vals = ite[0]
        kids = ite[-1][0]
        parts = ite[-1][-1]
        type = news_vals["type"]
        try:
            parent = news_dict.get(type).objects.create(**news_vals)
            if kids and type in ("story", "poll"):
                get_children(type, kids, parent, Comment)
            if parts and type == "poll":
                get_children(type, parts, parent, PollOption)
        except Exception as e:
            print(e, " failed to generate")
            pass
    return None


def scheduled_tasks1():
    result = (fetch_news(top_news_link) + fetch_news(job_news_link))
    result = set(result)
    populate_database(result)