import yaml, requests
from IPython import embed
from bs4 import BeautifulSoup

titles = yaml.load(open("titles.yaml"))['titles']


def download_page(title):
    headers = {
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'en-US,en;q=0.8,tr;q=0.6',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
    }

    url = "http://www.imdb.com/title/%s/fullcredits" % title
    return requests.get(url, headers=headers)


def parse_response(title):
    response = download_page(title=title)
    return BeautifulSoup(response.text, "html5lib")


def parse_body(dom):
    return dom.find("div", {"id": "main"})


def parse_title(main_soap):
    return main_soap.find("h1", {"id": "subpage_title_block"}).find("h3").text


def parse_cast(main_soap):
    cast_list = main_soap.find("table", {"class": "cast_list"}).findAll("tr")
    for tr in cast_list:
        try:
            picture_td, actor_td, elipsis_td, episode_count_td = tr.findAll("td")
            actor_name = actor_td.find("span", {"itemprop": "name"}).text.strip()
            episode_count = int(episode_count_td.text.strip().split("episode")[0].split("(")[-1].strip())
            yield actor_name, episode_count
        except:
            pass


if __name__ == "__main__":
    title = titles[0]
    response_soap = parse_response(title)
    main_soap = parse_body(response_soap)
    actors = parse_cast(main_soap)
    embed()
