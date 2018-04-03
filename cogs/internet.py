from urllib.parse import quote as uriquote
from lxml import etree
import urllib.parse
import random
import time
import aiohttp
import feedparser
import asyncio

from discord.ext import commands
import discord

from .util.data_uploader import DataUploader
from .util.converters import CleanedCode
from .util.checks import right_channel
from .util.duckduckgo import DuckDuckGo


XKCD_ENDPOINT = 'https://xkcd.com/{}/info.0.json'
XKCD_RSS = 'https://xkcd.com/rss.xml'
BOTE_SPAM = 282500390891683841
VT_API = 'https://www.virustotal.com/vtapi/v2'

cog = None


class Internet:

    @staticmethod
    async def __local_check(ctx):
        return right_channel(ctx)

    def __init__(self, bot):
        self.bot = bot
        self.uploader_client = DataUploader(bot)
        self.xkcd_feed = feedparser.parse(XKCD_RSS)
        self.checker = bot.loop.create_task(self.check_xkcd())

        self.ddg = DuckDuckGo(bot)

    async def check_xkcd(self):
        while True:
            feed = feedparser.parse(XKCD_RSS, modified=self.xkcd_feed.modified)
            if feed.status == 200:
                if feed.entries[0].link != self.xkcd_feed.entries[0].link:
                    channel = self.bot.get_channel(BOTE_SPAM)
                    if channel is not None:
                        await channel.send(feed.entries[0].link)

                    self.xkcd_feed = feed

            await asyncio.sleep(600)

    @commands.command(aliases=['jake', 'sills', 'zwei'])
    async def dog(self, ctx):
        """Sends a picture of a random dog"""
        async with ctx.bot.session.get('http://random.dog/woof.json') as resp:
            json = await resp.json()
            await ctx.send(json['url'])

    @commands.command(aliases=['adam', 'b1nzy', 'spd'])
    async def cat(self, ctx):
        """Sends a picture of a random cat"""
        async with ctx.bot.session.get('https://aws.random.cat/meow') as resp:
            json = await resp.json()
            await ctx.send(json['file'])

    def parse_google_card(self, node):
        # Credit to Danny#0007 for this Google-card parsing code
        e = discord.Embed(colour=discord.Colour.blurple())

        calculator = node.find(".//span[@class='cwclet']")
        if calculator is not None:
            e.title = 'Calculator'
            result = node.find(".//span[@class='cwcot']")
            if result is not None:
                result = ' '.join((calculator.text, result.text.strip()))
            else:
                result = calculator.text + ' ???'
            e.description = result
            return e

        unit_conversions = node.xpath(".//input[contains(@class, '_eif') and @value]")
        if len(unit_conversions) == 2:
            e.title = 'Unit Conversion'

            xpath = etree.XPath("parent::div/select/option[@selected='1']/text()")
            try:
                first_node = unit_conversions[0]
                first_unit = xpath(first_node)[0]
                first_value = float(first_node.get('value'))
                second_node = unit_conversions[1]
                second_unit = xpath(second_node)[0]
                second_value = float(second_node.get('value'))
                e.description = ' '.join((str(first_value), first_unit, '=', str(second_value), second_unit))
            except Exception:
                return None
            else:
                return e

        if 'currency' in node.get('class', ''):
            currency_selectors = node.xpath(".//div[@class='ccw_unit_selector_cnt']")
            if len(currency_selectors) == 2:
                e.title = 'Currency Conversion'

                first_node = currency_selectors[0]
                first_currency = first_node.find("./select/option[@selected='1']")

                second_node = currency_selectors[1]
                second_currency = second_node.find("./select/option[@selected='1']")

                xpath = etree.XPath("parent::td/parent::tr/td/input[@class='vk_gy vk_sh ccw_data']")
                try:
                    first_value = float(xpath(first_node)[0].get('value'))
                    second_value = float(xpath(second_node)[0].get('value'))

                    values = (
                        str(first_value),
                        first_currency.text,
                        f'({first_currency.get("value")})',
                        '=',
                        str(second_value),
                        second_currency.text,
                        f'({second_currency.get("value")})'
                    )
                    e.description = ' '.join(values)
                except Exception:
                    return None
                else:
                    return e

        info = node.find(".//div[@class='_f2g']")
        if info is not None:
            try:
                e.title = ''.join(info.itertext()).strip()
                actual_information = info.xpath("parent::div/parent::div//div[@class='_XWk' or contains(@class, 'kpd-ans')]")[0]
                e.description = ''.join(actual_information.itertext()).strip()
            except Exception:
                return None
            else:
                return e

        translation = node.find(".//div[@id='tw-ob']")
        if translation is not None:
            src_text = translation.find(".//pre[@id='tw-source-text']/span")
            src_lang = translation.find(".//select[@id='tw-sl']/option[@selected='1']")

            dest_text = translation.find(".//pre[@id='tw-target-text']/span")
            dest_lang = translation.find(".//select[@id='tw-tl']/option[@selected='1']")

            e.title = 'Translation'
            try:
                e.add_field(name=src_lang.text, value=src_text.text, inline=True)
                e.add_field(name=dest_lang.text, value=dest_text.text, inline=True)
            except Exception:
                return None
            else:
                return e

        time = node.find("./div[@class='vk_bk vk_ans']")
        if time is not None:
            date = node.find("./div[@class='vk_gy vk_sh']")
            try:
                e.title = node.find('span').text
                e.description = f'{time.text}\n{"".join(date.itertext()).strip()}'
            except Exception:
                return None
            else:
                return e

        time = node.find("./div/div[@class='vk_bk vk_ans _nEd']")
        if time is not None:
            converted = "".join(time.itertext()).strip()
            try:
                parent = time.getparent()
                parent.remove(time)
                original = "".join(parent.itertext()).strip()
                e.title = 'Time Conversion'
                e.description = f'{original}...\n{converted}'
            except Exception:
                return None
            else:
                return e

        words = node.xpath(".//span[@data-dobid='hdw']")
        if words:
            lex = etree.XPath(".//div[@class='lr_dct_sf_h']/i/span")

            xpath = etree.XPath("../../../ol[@class='lr_dct_sf_sens']//" \
                                "div[not(@class and @class='lr_dct_sf_subsen')]/" \
                                "div[@class='_Jig']/div[@data-dobid='dfn']/span")
            for word in words:
                root = word.getparent().getparent()

                pronunciation = root.find(".//span[@class='lr_dct_ph']/span")
                if pronunciation is None:
                    continue

                lexical_category = lex(root)
                definitions = xpath(root)

                for category in lexical_category:
                    definitions = xpath(category)
                    try:
                        descrip = [f'*{category.text}*']
                        for index, value in enumerate(definitions, 1):
                            descrip.append(f'{index}. {value.text}')

                        e.add_field(name=f'{word.text} /{pronunciation.text}/', value='\n'.join(descrip))
                    except:
                        continue

            return e

        location = node.find("./div[@id='wob_loc']")
        if location is None:
            return None

        date = node.find("./div[@id='wob_dts']")
        category = node.find(".//img[@id='wob_tci']")
        xpath = etree.XPath(".//div[@id='wob_d']//div[contains(@class, 'vk_bk')]//span[@class='wob_t']")
        temperatures = xpath(node)
        misc_info_node = node.find(".//div[@class='vk_gy vk_sh wob-dtl']")

        if misc_info_node is None:
            return None

        precipitation = misc_info_node.find("./div/span[@id='wob_pp']")
        humidity = misc_info_node.find("./div/span[@id='wob_hm']")
        wind = misc_info_node.find("./div/span/span[@id='wob_tws']")

        try:
            e.title = 'Weather for ' + location.text.strip()
            e.description = f'*{category.get("alt")}*'
            e.set_thumbnail(url='https:' + category.get('src'))

            if len(temperatures) == 4:
                first_unit = temperatures[0].text + temperatures[2].text
                second_unit = temperatures[1].text + temperatures[3].text
                units = f'{first_unit} | {second_unit}'
            else:
                units = 'Unknown'

            e.add_field(name='Temperature', value=units, inline=False)

            if precipitation is not None:
                e.add_field(name='Precipitation', value=precipitation.text)

            if humidity is not None:
                e.add_field(name='Humidity', value=humidity.text)

            if wind is not None:
                e.add_field(name='Wind', value=wind.text)
        except:
            return None

        return e

    async def get_google_entries(self, query):
        url = f'https://www.google.com/search?q={uriquote(query)}'
        params = {
            'safe': 'on',
            'lr': 'lang_en',
            'hl': 'en'
        }

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) Gecko/20100101 Firefox/53.0'
        }

        # list of URLs and title tuples
        entries = []

        # the result of a google card, an embed
        card = None

        async with self.bot.session.get(url, params=params, headers=headers) as resp:
            if resp.status != 200:
                log.info('Google failed to respond with %s status code.', resp.status)
                raise RuntimeError('Google has failed to respond.')

            root = etree.fromstring(await resp.text(), etree.HTMLParser())

            # for bad in root.xpath('//style'):
            #     bad.getparent().remove(bad)

            # for bad in root.xpath('//script'):
            #     bad.getparent().remove(bad)

            # with open('google.html', 'w', encoding='utf-8') as f:
            #     f.write(etree.tostring(root, pretty_print=True).decode('utf-8'))

            """
            Tree looks like this.. sort of..
            <div class="rc">
                <h3 class="r">
                    <a href="url here">title here</a>
                </h3>
            </div>
            """

            card_node = root.xpath(".//div[@id='rso']/div[@class='_NId']//" \
                                   "div[contains(@class, 'vk_c') or @class='g mnr-c g-blk' or @class='kp-blk']")

            if card_node is None or len(card_node) == 0:
                card = None
            else:
                card = self.parse_google_card(card_node[0])

            search_results = root.findall(".//div[@class='rc']")
            # print(len(search_results))
            for node in search_results:
                link = node.find("./h3[@class='r']/a")
                if link is not None:
                    # print(etree.tostring(link, pretty_print=True).decode())
                    entries.append((link.get('href'), link.text))

        return card, entries

    @commands.command(aliases=['g'])
    async def google(self, ctx, *, query):
        '''Searches google and gives you top result.'''
        await ctx.trigger_typing()
        try:
            card, entries = await self.get_google_entries(query)
        except RuntimeError as e:
            await ctx.send(str(e))
        else:
            if card:
                value = '\n'.join(f'[{title}]({url.replace(")", "%29")})' for url, title in entries[:3])
                if value:
                    card.add_field(name='Search Results', value=value, inline=False)
                return await ctx.send(embed=card)

            if len(entries) == 0:
                return await ctx.send('No results found... sorry.')

            next_two = [x[0] for x in entries[1:3]]
            first_entry = entries[0][0]
            if first_entry[-1] == ')':
                first_entry = first_entry[:-1] + '%29'

            if next_two:
                formatted = '\n'.join(f'<{x}>' for x in next_two)
                msg = f'{first_entry}\n\n**See also:**\n{formatted}'
            else:
                msg = first_entry

        await ctx.send(msg)

    @commands.command(aliases=['wa', 'alpha', 'wolfram_alpha'])
    async def wolfram(self, ctx, *, query: str):
        """Search Wolfram|Alpha for a query"""
        op = urllib.parse.urlencode({'i': query})
        await ctx.send('<https://www.wolframalpha.com/input/?{}>'.format(op))

    @commands.command()
    async def lucky(self, ctx, *, query: str):
        """I'm feeling lucky. Are you?"""
        op = urllib.parse.urlencode({'q': query})
        async with ctx.bot.session.get('https://google.com/search?{}&safe=active&&btnI'.format(op)) as resp:
            await ctx.send(resp.url)

    @commands.command(aliases=['paste.ee', 'upload'])
    async def paste(self, ctx, *, data: CleanedCode):
        """Upload data to https://paste.ee and return the URL"""

        if isinstance(ctx.channel, discord.abc.PrivateChannel):
            title = "{0.display_name}#{0.discriminator}".format(ctx.author)
        else:
            title = "{0.display_name}#{0.discriminator} in #{1}".format(ctx.author, ctx.channel.name)

        url = await self.uploader_client.upload(
                    data,
                    title
                )
        await ctx.send('{0.mention} {1}'.format(ctx.author, url))
        if not isinstance(ctx.channel, discord.abc.PrivateChannel):
            await ctx.message.delete()

    async def post_comic(self, ctx: commands.Context, metadata: 'Dict[str, Any]', comic_number: int):
        embed = discord.Embed(title='#{}'.format(metadata['num']), description=metadata['safe_title'],
                              url='https://xkcd.com/{}/'.format(metadata['num']), colour=0xFFFFFF)
        embed.set_image(url=metadata['img'])
        embed.set_footer(text=metadata['alt'])

        await ctx.send(embed=embed)

    async def fetch_comic_data(self, number=None, *, latest=False):
        async with self.bot.session.get(XKCD_ENDPOINT.format(number if not latest else '')) as resp:
            return await resp.json()

    @commands.group(invoke_without_command=True)
    async def xkcd(self, ctx, *, comic_number: int):
        """ Shows an XKCD comic by comic number. """
        latest = await self.fetch_comic_data(latest=True)

        if comic_number > latest['num']:
            await ctx.send('Woah! Steady there tiger! There are only {} comics available. :cry:'.format(latest['num']))
            return
        elif comic_number < 1:
            await ctx.send('"Get strip number {}," they said, "It\'ll be easy."'.format(comic_number))
            return
        elif comic_number == 404:
            await ctx.send('`404`.. Really? What were you expecting??')
            return

        target = await self.fetch_comic_data(comic_number)

        await self.post_comic(ctx, target, comic_number)

    @xkcd.command()
    async def latest(self, ctx):
        """ Shows the latest XKCD comic. """
        latest = await self.fetch_comic_data(latest=True)
        await self.post_comic(ctx, latest, latest['num'])

    @xkcd.command()
    async def random(self, ctx):
        """ Shows a random XKCD comic. """
        latest = await self.fetch_comic_data(latest=True)
        comic_number = random.randint(1, latest['num'])
        target = await self.fetch_comic_data(comic_number)

        await self.post_comic(ctx, target, comic_number)

    @commands.command(aliases=['latency'])
    async def ping(self, ctx):
        """Views websocket and message send latency."""
        # Websocket latency
        results = []
        for shard in ctx.bot.shards.values():
            ws_before = time.monotonic()
            await (await shard.ws.ping())
            ws_after = time.monotonic()
            results.append(round((ws_after - ws_before) * 1000))

        # Message send latency
        rtt_before = time.monotonic()
        message = await ctx.send('Ping...')
        rtt_after = time.monotonic()

        rtt_latency = round((rtt_after - rtt_before) * 1000)

        await message.edit(content='WS: **{0} ms**\nRTT: **{1} ms**'.format(', '.join(map(str, results)), rtt_latency))

    @commands.command(aliases=['scan'])
    @commands.cooldown(4, 60)
    async def virustotal(self, ctx, url):
        """Scan a url"""
        key_file = self.bot.config['virustotal'].get('key_file')
        with open(key_file) as f:
            key = f.read().split('\n')[0].strip()

        params = {'apikey': key, 'url': url}
        async with aiohttp.ClientSession() as session:
            async with session.post(VT_API+'/url/scan', data=params) as request:
                response = await request.json()

        if response['response_code'] == -1:
            await ctx.send('Invalid url.')
        elif 'permalink' not in response:
            await ctx.send('Search failed. Are you sure you entered a valid url?')
        else:
            await ctx.send(f'Scan results found.\n{response["permalink"]}')

    @commands.command(alias=['imagesearch'])
    async def image(self, ctx, *, query: str):
        """Search the internet for a nice image for you"""

        image = await self.ddg.get_image(query)
        if image is None:
            return await ctx.send('No results found')

        await ctx.send(':outbox_tray: Sent to DMs.')
        return await ctx.author.send(f':inbox_tray: I found {image}')

    @commands.command(alias=['square_i'])
    async def squarei(self, ctx, *, query: str):
        """Search the internet for a nice square picture for you"""

        image = await self.ddg.get_pfp_image(query)
        if image is None:
            return await ctx.send('No results found')

        return await ctx.send(f'I found {image}')


def setup(bot):
    global cog
    bot.add_cog(Internet(bot))
    cog = bot.cogs['Internet']

def teardown(bot):
    global cog
    cog.checker.close()
