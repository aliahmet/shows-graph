import json

import yaml, requests
import os
from IPython import embed
from bs4 import BeautifulSoup

from helpers import show_progress, get_browser_headers

titles = yaml.load(open("titles.yaml"))['titles']

all_actors = {}
all_titles = {}
title_actors = {}
connections = {}
connections_list = {}


def download_page(title):
    headers = get_browser_headers()  # Avoid bot blocks
    url = "http://www.imdb.com/title/%s/fullcredits" % title  # Full Cast Page
    return requests.get(url, headers=headers).text  # Actually Get the page


def parse_response(title):
    """
    Download the page and feed it to Beatiful Soap
    :type title: str
    :return: BeautifulSoup
    """
    response = download_page(title=title)
    return BeautifulSoup(response, "html5lib")


def parse_body(dom):
    """
    Get the main div. DO it for faster search in the future
    :type dom: BeautifulSoup
    :return: BeautifulSoup
    """
    return dom.find("div", {"id": "main"})


def parse_title(main_soap):
    return main_soap.find("div", {"class": "subpage_title_block"}).find("h3").find("a").text


def parse_cast(main_soap):
    first_count = None
    cast_list = main_soap.find("table", {"class": "cast_list"}).findAll("tr")
    for tr in cast_list:
        tds = tr.findAll("td")
        if len(tds) != 4:
            continue
        picture_td, actor_td, elipsis_td, episode_count_td = tds
        actor_name = actor_td.find("span", {"itemprop": "name"}).text.strip()
        actor_link = actor_td.find("a").attrs['href'].split("/")[2]
        episode_count = int(episode_count_td.text.strip().split("episode")[0].split("(")[-1].strip())
        if first_count is None:
            first_count = episode_count
        existance = episode_count / first_count
        all_actors[actor_link] = actor_name
        yield actor_link, actor_name, episode_count, existance


if __name__ == "__main__":
    total = len(titles)
    for i, title in enumerate(titles):
        show_progress(i, total, title)
        response_soap = parse_response(title)

        main_soap = parse_body(response_soap)

        name = parse_title(main_soap)
        show_progress(i, total, title + " (" + name + ")")
        all_titles[title] = name

        cast_table = parse_cast(main_soap)
        actors = set([x[0] for x in cast_table])
        for other_title, other_actors in title_actors.items():
            connections[(other_title, title)] = len(other_actors & actors)
            connections_list[(other_title, title)] = other_actors & actors
        title_actors[title] = actors
    connections_graph = [{
                             "source": x[0],
                             "source_name": all_titles[x[0]],
                             "to": x[1],
                             "to_name": all_titles[x[1]],
                             "weight": len(y),
                             "actors": [all_actors[x] for x in list(y)]
                         } for (x, y) in connections_list.items() if len(y) != 0]

    open("people.json", "w").write(json.dumps(all_actors, ensure_ascii=False, indent=4))
    open("titles.json", "w").write(json.dumps(all_titles, ensure_ascii=False, indent=4))
    open("connections.json", "w").write(json.dumps(connections_graph, ensure_ascii=False, indent=4))
