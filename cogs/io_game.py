import inspect
import io

import discord

from PIL import Image, ImageDraw, ImageFont
from discord.ext import commands

from config.io_game import rounds


firstOrDefault = lambda self, x=None: self[0] if self else x
first = lambda self, func, default=None: firstOrDefault((*filter(func, self),), default)


class IO_Game:
    FONT = 'config/aa2.ttf'

    BORDER_WIDTH = 2
    CELL_PADDING = 3
    FONT_SIZE = 18

    BORDER_COL = (127, 127, 127)
    FONT_COL = (0  , 0  , 0  )
    DBG_COL = (175, 175, 175)
    BG_COL = (200, 200, 200)

    SUBMISSION_CHANNEL = 364571585081901056

    def __init__(self, bot):
        self.bot = bot

        self.status = {
            # userid: {
            #     round: [(in, in, out, out), "Hint used", (in, in, out, out), "Thing"]
            # }
        }
        self.submission_queue = {
            # queue_message: (ctx, ans, q_msg, round)
        }

        self.font = ImageFont.truetype(self.FONT, self.FONT_SIZE)

    def render_table(self, table):
        col_widths = []
        full_widths = []

        for row in table:
            if isinstance(row, (tuple, list)):
                col_widths.append((*(self.font.getsize(str(i))[0] for i in row),))
            else:
                full_widths.append(self.font.getsize(str(row))[0] + \
                                   self.CELL_PADDING * 2 + self.BORDER_WIDTH * 2)

        col_widths = [max(i[x] for i in col_widths if len(i) > x)
                      for x in range(len(max(col_widths, key=len)))]

        im_width = max(max(full_widths), sum(col_widths) + self.BORDER_WIDTH + \
                self.BORDER_WIDTH * len(col_widths) + self.CELL_PADDING * 2 * len(col_widths))

        if im_width == max(full_widths):
            cw =  sum(col_widths) + self.BORDER_WIDTH + self.BORDER_WIDTH * \
                    len(col_widths) + self.CELL_PADDING * 2 * len(col_widths)
            for i in range(len(col_widths)):
                col_widths[i] += int(im_width - cw)
            cw =  sum(col_widths) + self.BORDER_WIDTH + self.BORDER_WIDTH * \
                    len(col_widths) + self.CELL_PADDING * 2 * len(col_widths)
            col_widths[-1] += im_width - cw


        row_height = int(self.CELL_PADDING * 2 + self.BORDER_WIDTH + self.FONT_SIZE * 1.5)

        im = Image.new('RGB', (im_width,
                               row_height * len(table) + self.BORDER_WIDTH))

        draw = ImageDraw.Draw(im)
        for n, row in enumerate(table):
            draw.rectangle(((0, row_height * n), (im_width - 1, row_height * (n + 1) + 1)),
                    self.BORDER_COL)
            draw.rectangle(((self.BORDER_WIDTH, row_height * n + self.BORDER_WIDTH),
                    (im_width - self.BORDER_WIDTH - 1, row_height * (n + 1) - self.BORDER_WIDTH)),
                    self.BG_COL)

            yp = row_height * n + self.BORDER_WIDTH 
            if isinstance(row, (tuple, list)):
                x = 0
                for m, i in enumerate(row):
                    x += self.BORDER_WIDTH + self.CELL_PADDING
                    text_size = self.font.getsize(str(i))

                    draw.text((((col_widths[m] - text_size[0]) / 2) + x,
                               yp + (row_height - text_size[1]) / 2),
                            str(i), font=self.font, fill=self.FONT_COL)
                    x += col_widths[m] + self.CELL_PADDING
                    if m != len(row) - 1:
                        draw.rectangle(((x, yp), (x + self.BORDER_WIDTH, yp + row_height)),
                                self.BORDER_COL)
            else:
                text_size = self.font.getsize(str(row))
                draw.text(((im_width - text_size[0]) / 2,
                           yp + (row_height - text_size[1]) / 2),
                          str(row), font=self.font, fill=self.FONT_COL)

        return im

    @commands.group(invoke_without_command=True)
    async def io(self, ctx):
        await ctx.send('Please choose an action')

    @io.command()
    async def diff(self, ctx, round_num:int):
        if round_num < 1 or round_num > len(rounds):
            return await ctx.send(f'Please enter a round number between 1 and {len(rounds)}')

        doc = rounds[round_num - 1].__doc__

        diff = first(doc.split('\n'), lambda x: x.strip().startswith('Difficulty:'), 'Difficulty: Unknown')
        diff = diff.strip().split('Difficulty:', 1)[1].strip()

        await ctx.send(f'**Difficulty:** {diff}')

    @io.command(name="status")
    async def stats(self, ctx, round_num:int):
        if round_num < 1 or round_num > len(rounds):
            return await ctx.send(f'Please enter a round number between 1 and {len(rounds)}')

        round_num -= 1
        if ctx.author.id not in self.status:
            self.status[ctx.author.id] = {}

        if round_num not in self.status[ctx.author.id]:
            self.status[ctx.author.id][round_num] = []

        status = self.status[ctx.author.id][round_num]

        doc = rounds[round_num].__doc__
        name = doc.strip().split('\n')[0].strip()

        params = [i[0] for i in inspect.signature(rounds[round_num]).parameters]
        returns = inspect.signature(rounds[round_num]).return_annotation

        table = [name, (*params, *(i.__name__ for i in returns))]
        for row in status:
            table.append(row)

        img = self.render_table(table)

        image_file = io.BytesIO()
        img.save(image_file, format='png')
        image_file.seek(0)

        d_file = discord.File(fp=image_file, filename='image.png')
        await ctx.send(files=[d_file])

    @io.command()
    async def hint(self, ctx, round_num:int):
        if round_num < 1 or round_num > len(rounds):
            return await ctx.send(f'Please enter a round number between 1 and {len(rounds)}')
        
        doc = rounds[round_num - 1].__doc__

        hint = first(doc.split('\n'), lambda x: x.strip().startswith('Hint:'), 'Hint: No hint avaliable')
        hint = hint.strip().split('Hint:', 1)[1].strip()

        name = doc.strip().split('\n')[0].strip()

        await ctx.send(f'Hint for round **{name}**:\n{hint}')
        if ctx.author.id not in self.status:
            self.status[ctx.author.id] = {}
        if round_num - 1 not in self.status[ctx.author.id]:
            self.status[ctx.author.id][round_num - 1] = []

        self.status[ctx.author.id][round_num - 1].append(f'Hint: {hint}')

    @io.command()
    async def test(self, ctx, round_num: int, *args:int):
        if round_num < 1 or round_num > len(rounds):
            return await ctx.send(f'Please enter a round number between 1 and {len(rounds)}')
    
        doc = rounds[round_num - 1].__doc__
        name = doc.strip().split('\n')[0].strip()

        try:
            out = rounds[round_num - 1](*args)
        except TypeError:
            return await ctx.send('Unexpected number of arguments to function')

        if not isinstance(out, (tuple, list)):
            out = (out,)

        await ctx.send(f'For round **{name}** with inputs **{", ".join(str(i) for i in args)}**:\n'
                       f'**{", ".join(str(i) for i in out)}**')

        if ctx.author.id not in self.status:
            self.status[ctx.author.id] = {}
        if round_num - 1 not in self.status[ctx.author.id]:
            self.status[ctx.author.id][round_num - 1] = []

        self.status[ctx.author.id][round_num - 1].append((*args, *out))

    @io.command()
    async def submit(self, ctx, round_num: int, *, answer):
        if round_num < 1 or round_num > len(rounds):
            return await ctx.send(f'Please enter a round number between 1 and {len(rounds)}')
    
        doc = rounds[round_num - 1].__doc__
        ans = first(doc.split('\n'), lambda x: x.strip().startswith('Solution:'), 'Solution: No clue')
        ans = ans.strip().split('Solution:', 1)[1].strip()

        chan = self.bot.get_channel(self.SUBMISSION_CHANNEL)

        q = await chan.send(f'Sumbmissions from {ctx.author.mention}:\n{answer}\nCorrect solution:\n{ans}')
        self.submission_queue[q.id] = (ctx, answer, q, round_num - 1)
        await q.add_reaction('✅')
        await q.add_reaction('❌')

        await ctx.send('Answer recorded. Please wait for a moderator to review it.')

        if ctx.author.id not in self.status:
            self.status[ctx.author.id] = {}
        if round_num - 1 not in self.status[ctx.author.id]:
            self.status[ctx.author.id][round_num - 1] = []

        self.status[ctx.author.id][round_num - 1].append(f'Submitted {answer}')

    async def on_reaction_add(self, reaction, user):
        if user.bot:
            return

        if reaction.message.id in self.submission_queue:
            ctx, answer, q, rn = self.submission_queue.pop(reaction.message.id)

            if reaction.emoji == '✅':
                await ctx.send(f'Your submission of {answer} was correct!')
                self.status[ctx.author.id][rn].append(f'Answer {answer} correct!')
            else:
                await ctx.send(f'Your submission of {answer} was incorrect.')
                self.status[ctx.author.id][rn].append(f'Answer {answer} incorrect.')

            await q.delete()


def setup(bot):
    bot.add_cog(IO_Game(bot))

