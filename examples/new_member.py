# This example requires the 'members' privileged intents

import nextcord

from nextcord.ext import commands

class MyClient(commands.Bot):
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

    async def on_member_join(self, member: nextcord.Member):
        guild = member.guild
        if guild.system_channel is not None:
            to_send = f'Welcome {member.mention} to {guild.name}!'
            await guild.system_channel.send(to_send)


intents = nextcord.Intents.default()
intents.members = True

bot = MyClient(intents=intents)
bot.run('token')
