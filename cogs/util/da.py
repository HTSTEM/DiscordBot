import random
import json
import os

import deviantart


PAGINATE_SIZE = 10
ANIMOO = 'minimalistic-animoo'
CACHE_FILE = 'da_cache.json'


class DeviationCollector:
    def __init__(self, bot):
        self.bot = bot

        self.config = self.bot.config.get('deviantart', {})

        self.da = deviantart.Api(self.config.get('client_id'), self.config.get('client_secret'))

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
            has_more = True
            offset = 0
            while has_more:
                res = self.da.get_gallery_folder(ANIMOO, folder['folderid'], limit=PAGINATE_SIZE, offset=offset)
                for r in res['results']:
                    if r.content is not None and 'src' in r.content:
                        self.deviations.add(r.content.get('src'))

                has_more = res['has_more']
                offset = res['next_offset']

            self.bot.logger.info(f' - {n + 1}/{len(folders)} folders..')

        self.deviations = list(self.deviations)

    def _get_random_deviation(self):
        deviation = None
        while deviation is None:
            deviation = random.choice(self.deviations)

        return deviation

    async def get_random_deviation(self, loop):
        return await loop.run_in_executor(None, self._get_random_deviation)
