# Std Lib Imports
pass

# 3rd Party Imports
import discord
from discord.ext.commands import Cog, command, has_any_role
import databases

# Local Imports
from utils import load_config, cog_error_handler
from utils.emojis import success, warning, error, info, loading
from utils.discord import not_nobot_role


global_config = load_config()
config = global_config.cogs.vip

class VIP(Cog):
    cog_command_error = cog_error_handler

    @command(aliases=config.upgrade.aliases, help=config.upgrade.help)
    @has_any_role(*config.upgrade.role_names)
    @not_nobot_role()
    async def upgrade(self, ctx):
        database = databases.Database(global_config.databases.tf2maps_site)
        await database.connect()

        query = "SELECT user_id FROM xf_user_field_value WHERE field_id = :field_id AND field_value = :field_value"
        values = {"field_id": "discord_user_id", "field_value": ctx.author.id}
        result = await database.fetch_one(query=query, values=values)

        if not result:
            await ctx.reply(f"{error} You don't seem to have a Discord User ID # set in your TF2Maps.net profile.\nSee here on how to get started: http://bot.tf2maps.net/faq.php'")
            return

        query = "SELECT secondary_group_ids FROM xf_user WHERE user_id = :user_id AND find_in_set(:vip_gid, secondary_group_ids)"
        values = {"user_id": result[0], "vip_gid": 19}
        result = await database.fetch_one(query=query, values=values)

        if not result:
            await ctx.reply(f"{error} You must be a VIP user on TF2Maps.net for the discord VIP Role.")
            return

        vip_role = discord.utils.get(ctx.guild.roles, name="VIP")

        if vip_role in ctx.author.roles:
            await ctx.send(f"{warning} You're already a VIP, go away.")
            return

        await ctx.author.add_roles(vip_role)
        await ctx.reply(f"{info} You are now a :star2: TF2Maps Discord VIP :star2: ")
