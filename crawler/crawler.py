import json
import os
from collections import OrderedDict

import yaml, requests
import os
from IPython import embed
from bs4 import BeautifulSoup

from helpers import show_progress, get_browser_headers

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

titles = yaml.load(open("titles.yaml"))['titles']

all_actors = {}
all_titles = {}
title_actors = {}
connections = {}
connections_list = {}


def download_page(title, invalidate_cache=False):
    text = None
    cache_file = os.path.join(BASE_DIR, "cache", title + ".html")
    if invalidate_cache:
        os.unlink(cache_file)

    if not os.path.exists(cache_file):
        url = "http://www.imdb.com/title/%s/fullcredits" % title  # Full Cast Page
        text = requests.get(url, headers=get_browser_headers()).text  # Actually Get the page
        dom = BeautifulSoup(text, "lxml")
        text = dom.find("div", {"id": "main"}).decode()
        open(cache_file, "w").write(text)

    if not text:
        text = open(cache_file).read()

    return text


def parse_response(title, invalidate_cache=False):
    """
    Download the page and feed it to Beatiful Soap
    :type title: str
    :return: BeautifulSoup
    """
    response = download_page(title=title, invalidate_cache=invalidate_cache)
    return BeautifulSoup(response, "lxml")


def parse_body(dom):
    """
    Get the main div. DO it for faster search in the future
    :type dom: BeautifulSoup
    :return: BeautifulSoup
    """
    return dom.find("div", {"id": "main"})


def parse_title(main_soap):
    return main_soap.find("div", {"class": "subpage_title_block"}).find("h3").find("a").text


def parse_character_name_and_count(td):
    content = td.text.strip()
    if "/" in content:
        character_name = content.split("/")[0].strip()
    elif "(" in content:
        character_name = content.split("(")[0].strip()
    else:
        character_name = "Unknown"

    episode_count = int(content.split("episode")[0].split("(")[-1].strip())
    return character_name, episode_count


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
        character_name, episode_count = parse_character_name_and_count(episode_count_td)
        if first_count is None:
            first_count = episode_count
        existance = episode_count / first_count
        all_actors[actor_link] = actor_name
        yield actor_link, actor_name, episode_count, existance, character_name


def generate_jsons():
    connections_graph = []
    for (x, y) in connections_list.items():
        if len(y) != 0:
            connection = OrderedDict()
            connection["source_name"] = all_titles[x[0]]
            connection["target_name"] = all_titles[x[1]]
            connection["source"] = x[0]
            connection["target"] = x[1]
            connection["actor_count"] = len(y)
            connection["actors"] = y

            connections_graph.append(connection)

    open("people.json", "w").write(json.dumps(all_actors, ensure_ascii=False, indent=4))
    open("titles.json", "w").write(json.dumps(all_titles, ensure_ascii=False, indent=4))
    open("connections.json", "w").write(json.dumps(connections_graph, ensure_ascii=False, indent=4))


def intersect(actor_set_1, actor_set_2):
    actors = []
    for actor_1 in actor_set_1:
        for actor_2 in actor_set_2:
            id_1 = actor_1[0]
            id_2 = actor_2[0]
            c1 = actor_1[2]
            a2 = actor_2[1]
            c2 = actor_2[2]
            if id_1 != id_2:
                # Isim benzeligi olabilir o yuzden idler
                continue
            if c1 * c2 < 5:
                continue

            actors.append([actor_2[1], actor_1[4], actor_2[4]])
    return actors


def main():
    total = len(titles)
    for i, title in enumerate(titles):
        show_progress(i, total, title)
        main_soap = parse_response(title)
        name = parse_title(main_soap)
        show_progress(i, total, title + " (" + name + ")")
        all_titles[title] = name

        cast_table = list(parse_cast(main_soap))
        for other_title, other_actors in title_actors.items():
            actor_set_1 = other_actors
            actor_set_2 = cast_table
            mutual_actors = intersect(actor_set_1, actor_set_2)
            connections[(other_title, title)] = len(mutual_actors)
            connections_list[(other_title, title)] = mutual_actors

        title_actors[title] = cast_table
    show_progress(total, total, "Finished", True)
    generate_jsons()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Keyboard Interrupt")
        exit(0)
