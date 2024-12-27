import os
import random
import discord
import shapefile
from shapely.geometry import Point, shape
from config import *

class StreetView(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.current_image = None
        self.current_coords = None

    @commands.command(name="streetview", aliases=["sv"], help="")
    async def streetview(self, ctx, *args):
        if not ctx.guild:
            return

        await self.send_random_image(ctx)

    @commands.command(name="g", help="")
    async def guess(self, ctx, *args):
        if not ctx.guild or not self.current_image or not self.current_coords:
            return

        guessed_country = " ".join(args).lower()

        if self.is_correct_guess(guessed_country):
            await ctx.message.add_reaction("✅")
            await self.send_random_image(ctx)
        else:
            await ctx.message.add_reaction("❌")

    @commands.command(name="end", help="")
    async def stop(self, ctx):
        if not ctx.guild:
            return

        self.current_image = None
        self.current_coords = None
        await ctx.send("The street view guessing game has been ended.")

    async def send_random_image(self, ctx):
        folder_path = STREETVIEW_FOLDER
        
        try:
            random_image = random.choice(os.listdir(folder_path))
            while not os.path.isfile(os.path.join(folder_path, random_image)):
                random_image = random.choice(os.listdir(folder_path))
        except IndexError:
            await ctx.send("No images found in the folder.")
            return

        self.current_image = random_image
        try:
            lat_str, lng_str = random_image.rsplit('.', 1)[0].split('_')
            lat = float(lat_str.replace('_', '.'))
            lng = float(lng_str.replace('_', '.'))
        except ValueError:
            await ctx.send("Invalid image filename format.")
            return

        self.current_coords = Point(lng, lat)

        image_path = os.path.join(folder_path, random_image)

        embed = discord.Embed(title="Guess the Country", color=discord.Color.blue())
        file = discord.File(image_path, filename=random_image)
        embed.set_image(url=f"attachment://{random_image}")

        await ctx.send(file=file, embed=embed)

    def is_correct_guess(self, guessed_country):
        shapefile_path = SHAPEFILE
        sf = shapefile.Reader(shapefile_path, encoding='iso-8859-1')
        for record, shape_rec in zip(sf.records(), sf.shapes()):
            if record["NAME"].lower() == guessed_country or record["ISO2"].lower() == guessed_country:
                if shape(shape_rec).contains(self.current_coords):
                    return True
        return False

async def setup(bot):
    await bot.add_cog(StreetView(bot))
