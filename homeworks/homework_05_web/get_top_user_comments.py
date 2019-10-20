import asyncio
import aiohttp
import csv
import sys


from collections import Counter
from bs4 import BeautifulSoup


def r_run(aw):
    if sys.version_info >= (3, 7):
        return asyncio.run(aw)

    # Emulate asyncio.run() on older versions
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(aw)
    finally:
        loop.close()
        asyncio.set_event_loop(None)


async def get_html(link):
    async with aiohttp.ClientSession() as session:
        async with session.get(link) as response:
            return link, await response.text()


async def main_coro(links):
    return await asyncio.gather(*[
        get_html(link) for link in links
    ])


def parse_html(text):
    html = BeautifulSoup(text, 'html.parser')
    return Counter((
        span.getText()
        for span in html.findAll('span', attrs={'class': 'user-info__nickname_comment'})
    )).most_common()


def write_csv(data, filename):
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerows(data)


def main(links, filename):
    lines = [['link', 'username', 'count_comment']]
    for link, text in r_run(main_coro(links)):
        for username, count_comment in parse_html(text):
            lines.append([link, username, count_comment])
    write_csv(lines)


if __name__ == '__main__':
    filename = 'top_user_comments.csv'
    links = sys.argv[1:4]
    main(links, filename)
