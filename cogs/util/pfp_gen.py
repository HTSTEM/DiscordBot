import random
import json
import re


class PFPGrabber:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.session
    
    async def _search(self, keywords):
        url = 'https://duckduckgo.com/'
        params = {'q': keywords}

        async with self.session.post(url, data=params) as response:
            data = await response.text()
            search_obj = re.search(r'vqd=(\d+)&', data, re.M | re.I)

        if search_obj is None:
            return []

        headers = {
            'dnt': '1',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'x-requested-with': 'XMLHttpRequest',
            'accept-language': 'en-GB,en-US;q=0.8,en;q=0.6,ms;q=0.4',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'referer': 'https://duckduckgo.com/',
            'authority': 'duckduckgo.com',
        }

        params = (
            ('l', 'wt-wt'),
            ('o', 'json'),
            ('q', keywords),
            ('vqd', search_obj.group(1)),
            ('f', ',,,'),
            ('p', '2'),
            ('t', 'hf'),
            ('iaf', 'layout:aspect-square')
        )

        request_url = url + "i.js"
        
        async with self.session.get(request_url, params=params, headers=headers) as response:
            data = await response.text()
            
            jdata = json.loads(data)
            
            return jdata.get('results')
    
    async def get_image(self, term):
        term = f'{term} profile picture'
        
        results = await self._search(term)
        random.shuffle(results)
        
        best = (None, 0)
        for r in results:
            ar = r.get('width') / r.get('height')
            if abs(1 - best[1]) > abs(1 - ar) + 0.2:  # Make it slightly lenient
                best = (r.get('image'), ar)
        
        return best[0]
