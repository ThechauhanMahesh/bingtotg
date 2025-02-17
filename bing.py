import asyncio
import urllib.request
import urllib
import aiohttp
import re
from pyrogram import Client, filters
from pyrogram.errors import FloodPremiumWait, FloodWait
from pyrogram.types import Message

class Config(object):
    API_ID = 2992000
    API_HASH = "235b12e862d71234ea222082052822fd"
    CHANNEL_ID = -1002463705087
    BOT_TOKEN = "7470662339:AAGnk3kBpPlZRwyIvI_uplduavaQziUNCUQ"
    AUTH_USERS = [7197823043]

jvbot = Client("bot", Config.API_ID, Config.API_HASH, bot_token=Config.BOT_TOKEN)

class Bing:
    def __init__(self, query, limit, adult='on', filter='', client: Client = None, verbose: bool=True,):
        self.download_count = 0
        self.query = query
        self.adult = adult
        self.filter = filter
        self.client = client
        self.verbose = verbose
        self.seen = set()

        assert type(limit) == int, "limit must be integer"
        self.limit = limit

        # self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        self.page_counter = 0
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) ' 
      'AppleWebKit/537.11 (KHTML, like Gecko) '
      'Chrome/23.0.1271.64 Safari/537.11',
      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
      'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
      'Accept-Encoding': 'none',
      'Accept-Language': 'en-US,en;q=0.8',
      'Connection': 'keep-alive'}


    def get_filter(self, shorthand):
            if shorthand == "line" or shorthand == "linedrawing":
                return "+filterui:photo-linedrawing"
            elif shorthand == "photo":
                return "+filterui:photo-photo"
            elif shorthand == "clipart":
                return "+filterui:photo-clipart"
            elif shorthand == "gif" or shorthand == "animatedgif":
                return "+filterui:photo-animatedgif"
            elif shorthand == "transparent":
                return "+filterui:photo-transparent"
            else:
                return ""


    async def save_image(self, link):
        if self.verbose:
            print(f"[!] Downloading: {self.download_count} {link}")
        try:
            await self.client.send_photo(Config.CHANNEL_ID, link)
            self.download_count += 1
            if self.verbose:
                print("[+] Uploaded image.")
            await asyncio.sleep(1)
        except (FloodWait, FloodPremiumWait) as e:
            print(f"[!] FloodWait: {e.value}")
            await asyncio.sleep(e.value)
            return await self.save_image(link)
        except Exception as e:
            print(f"[!] Error: {e}")


    async def run(self):
        async with aiohttp.ClientSession() as session:
            while self.download_count < self.limit:
                if self.verbose:
                    print('\n\n[!!]Indexing page: {}\n'.format(self.page_counter + 1))
                request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(self.query) \
                              + '&first=' + str(self.page_counter) + '&count=' + str(self.limit) \
                              + '&adlt=' + self.adult + '&qft=' + ('' if self.filter is None else self.get_filter(self.filter))
                request = await session.get(request_url, headers=self.headers)
                html = await request.text()
                if html == "":
                    return "[%] No more images are available"
                links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)
                if self.verbose:
                    print("[%] Indexed {} Images on Page {}.".format(len(links), self.page_counter + 1))
                    print("\n===============================================\n")

                tasks = []
                for link in links:
                    if self.download_count < self.limit and link not in self.seen:
                        self.seen.add(link)
                        tasks.append(self.save_image(link))

                await asyncio.gather(*tasks)

                self.page_counter += 1
            return "\n\n[%] Done. Uploaded {} images.".format(self.download_count)


@jvbot.on_message(filters.command("bing") & filters.user(Config.AUTH_USERS))
async def scraper(c: Client, m: Message):
    if Config.CHANNEL_ID == 0:
        return await m.reply_text("Please set the Channel ID first")
    try:
        _, limit, query = m.text.split(" ", 2)
    except ValueError:
        return await m.reply_text("Invalid Command")
    limit = int(limit)
    rr: Message = await m.reply_text(f"Processing for {limit} images of {query}")
    bing = Bing(query, limit, client=c)
    res = await bing.run()
    await rr.edit(text=res)

@jvbot.on_message(filters.command("start") & filters.user(Config.AUTH_USERS))
async def start(c: Client, m: Message):
    await m.reply_text("I am alive")

@jvbot.on_message(filters.command("chat") & filters.user(Config.AUTH_USERS))
async def chnageChat(c,m: Message):
    _, id = m.text.split(" ", 1)
    if not id.isnumeric():
        return await m.reply_text("Invalid Chat ID")
    Config.CHANNEL_ID = int(id)
    await m.reply_text(f"Chat ID Updated to {id}")



jvbot.run()
