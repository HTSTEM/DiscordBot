import random
import json
import os

from fuzzywuzzy import process
import deviantart


PAGINATE_SIZE = 10
ANIMOO = 'minimalistic-animoo'
CACHE_FILE = 'state_cache/da_cache.json'


class DeviationCollector:
    def __init__(self, bot):
        self.bot = bot

        self.config = self.bot.config.get('deviantart', {})

        secret_file = self.config.get('client_secret_file')
        with open(secret_file) as f:
            secret = f.read().split('\n')[0].strip()

        self.da = deviantart.Api(self.config.get('client_id'), secret)

        if not os.path.exists(CACHE_FILE):
            self.generate_cache()
        else:
            self.load_cache()

    def generate_cache(self):
        self.bot.logger.info('Locating DA folders..')
        folders = self.reload_folder_cache()
        self.bot.logger.info('Caching deviations..')
        self.reload_deviation_cache(folders)
        self.bot.logger.info(f'Cached {len(self.deviations)} deviations!')

        with open(CACHE_FILE, 'w') as f:
            json.dump(self.deviations, f)

    def load_cache(self):
        with open(CACHE_FILE, 'r') as f:
            self.deviations = json.load(f)

    def reload_folder_cache(self):
        folders = []

        has_more = True
        offset = 0
        while has_more:
            res = self.da.get_gallery_folders(ANIMOO, limit=PAGINATE_SIZE, offset=offset)
            folders += res['results']
            has_more = res['has_more']
            offset = res['next_offset']

        return folders

    def reload_deviation_cache(self, folders):
        self.deviations = set()

        for n, folder in enumerate(folders):
            if folder['name'] == 'Featured':
                continue

            has_more = True
            offset = 0
            while has_more:
                res = self.da.get_gallery_folder(ANIMOO, folder['folderid'], limit=PAGINATE_SIZE, offset=offset)
                for r in res['results']:
                    if r.content is not None and 'src' in r.content:
                        self.deviations.add((r.content.get('src'), r.title, folder['name']))

                has_more = res['has_more']
                offset = res['next_offset']

            self.bot.logger.info(f' - {n + 1}/{len(folders)} folders..')

        self.deviations = list(self.deviations)

    async def get_deviation(self, loop, search_term):
        deviation = await self._get_deviation(loop, search_term)
        return f'I found **{deviation[1]}** from **{deviation[2]}**:\n{deviation[0]}'

    async def _get_deviation(self, loop, search_term):
        search_term = search_term.strip()
        anime = False
        if search_term.startswith('a:'):
            search_term = search_term[2:]
            anime = True

        if not search_term:
            return random.choice(self.deviations)

        if anime:
            folders = set()
            for i in self.deviations:
                folders.add(i[2])
            folder = process.extractOne(search_term, folders)[0]

            return random.choice([i for i in self.deviations if i[2] == folder])

        return process.extractOne(search_term, self.deviations, processor=lambda x:x[1])[0]
