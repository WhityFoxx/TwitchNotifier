from twitchapi.notifier import Twitch
from config import CLIENT_ID, CLIENT_SECRET, CHANNEL_NOTIFICATION, PING_ROLE_ID
import discord
import sqlite3
from discord.ext import tasks
from discord.ext import commands
import datetime
from discord.utils import format_dt




class NotifierCog(commands.Cog):
    def __init__(self, bot):
        self.bot =bot
        self.connection = sqlite3.connect('databases/twitch.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS channels (channel_id TEXT PRIMARY KEY, is_live BOOLEAN, mention TEXT)')
        self.twitch = Twitch(CLIENT_ID, CLIENT_SECRET)
        self.token = None
        self.init_time = datetime.datetime.utcnow()
        
        self.update_token.start()
    @tasks.loop(seconds=60)
    async def check_live(self):
        self.cursor.execute('SELECT * FROM channels')
        channels = self.cursor.fetchall()
        channel = await self.bot.fetch_channel(CHANNEL_NOTIFICATION)
        for user in channels:
            try:
                stream_status = await self.twitch.get_stream_status(self.token, user[0])
                if stream_status['data'][0]['type'] == 'live':
                    date = datetime.datetime.strptime(stream_status['data'][0]['started_at'], "%Y-%m-%dT%H:%M:%SZ") - self.init_time
                    if user[1] == False :
                        embed = discord.Embed(title=stream_status['data'][0]["title"],description=f'Стрим начался {format_dt(datetime.datetime.now() + date,"R")}', url=f"https://www.twitch.tv/{user[0]}", color=0xFFC0CB)
                        embed.set_footer(text='Example Footer')
                        embed.add_field(name='Тематика', value=stream_status['data'][0]['game_name'], inline=False)
                        embed.add_field(name='Тэги', value=', '.join(stream_status['data'][0]['tags']), inline=False)
                        
                        width = '1280'
                        height = '720'
                        print()
                        embed.set_image(url=stream_status['data'][0]['thumbnail_url'].replace('{width}x{height}', f"{width}x{height}"))   
                        embed.set_thumbnail(url='https://i.imgur.com/1wl5ibp.png') # Example Image
                        await channel.send(f'<@&{PING_ROLE_ID}>, {user[2]} запустил трансляцию!',embed=embed)
                    self.cursor.execute('UPDATE channels SET is_live = 1 WHERE channel_id =?', (user[0],))
            except Exception as e:
                if not isinstance(e, IndexError):
                    print(f"Something went wrong in twitchcog: {e}")
                self.cursor.execute('UPDATE channels SET is_live = 0 WHERE channel_id =?', (user[0],))
            self.connection.commit()
    @tasks.loop(hours=1)
    async def update_token(self):
        self.token = await self.twitch.authorization()
        print('Token updated successfully!')
        

    @commands.Cog.listener()
    async def on_ready(self):
        print('Notifier Cog is ready!')
        
        self.check_live.start()
    @commands.slash_command()
    async def notify_add(self, ctx, user : discord.Option(discord.Member, 'Стример'),twitch_login: discord.Option(str, description='Логин пользователя')):
        self.cursor.execute('INSERT INTO channels (channel_id, is_live, mention) VALUES (?,?, ?)', (twitch_login, False, user.mention))
        self.connection.commit()
        await ctx.respond(f'Пользователь {twitch_login} добавлен в базу', ephemeral=True)

def setup(bot):
    bot.add_cog(NotifierCog(bot))
