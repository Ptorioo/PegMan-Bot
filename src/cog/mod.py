from config import *
import requests


class Mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_padlet(self, arg):
        result = []
        response = requests.get(PADLET_LINK)
        if response.status_code == 200:
            data = response.json()
            if arg == 0:
                for com in data['data']:
                    result.append(com['attributes']['headline'])
            else:
                if arg > len(data['data']):
                    arg = len(data['data'])
                for i in range(0, arg):
                    result.append(data['data'][i]['attributes']['headline'])
        else:
            result.append(f'Failed to connect to padlet. Error code: {response.status_code}')
        return result

    @commands.command()
    async def echo(self, ctx, role, *args):
        next_line = False
        if role.lower() == "everyone":
            role_mention = "@everyone"
            next_line = True
        elif role.lower() == "here":
            role_mention = "@here"
            next_line = True
        else:
            try:
                role_object = discord.utils.get(ctx.guild.roles, name=role)
                role_mention = role_object.mention
            except AttributeError:
                role_mention = role

        arg = " ".join(args)
        await ctx.send(f"{role_mention}" + next_line * "\n" + f" {arg}")
    
    @commands.command()
    async def padlet(self, ctx, *arg):
        if not arg:
            results = self.get_padlet(0)
            for result in results:
                await ctx.send(result)            
        elif arg[0] == 'all':
            results = self.get_padlet(0)
            for result in results:
                await ctx.send(result)
        elif arg[0].isnumeric():
            results = self.get_padlet(int(arg[0]))
            for result in results:
                await ctx.send(result)
        else:
            await ctx.send('Invalid request.')


async def setup(bot):
    await bot.add_cog(Mod(bot))
