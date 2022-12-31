import a2s
import discord
import asyncio
import time

auto_refresh_time = 60
url_connect = "https://hl2dm.community/connect/?"
url_thumbs  = "https://fastdl.hl2dm.community/maps/thumbs/"
botid       = 0
servers     = []
numServers  = 0
client      = discord.Client(intents=discord.Intents.default())

class Server:
    def __init__(self, name, icon, ip, port, override, channel, message, updatedate, updatetime):
        self.name = name
        self.icon = icon # prefix emoticon, used for country flags
        self.ip = ip
        self.port = port
        self.override = override # if True, hostname will be overriden by the server name you provided
        self.channel = channel # channel ID to broadcast status to
        self.message = message # set within function
        self.updatedate = updatedate # set within function
        self.updatetime = updatetime # set within function
        
class Player:
    def __init__(self, name, score, duration):
        self.name = name
        self.score = score
        self.duration = duration

# Connected time format consistent with game server browser:
def duration(seconds):
    h = seconds // 3600
    m = seconds % 3600 // 60
    s = seconds % 3600 % 60
    if(h):
        return f"{h}h {m}m {s}s"
    return f"{m}m {s}s"

############################
# DEFINE SERVERS HERE:

bot_token = "DISCORD_BOT_TOKEN"

servers.append (Server("Australian Deathmatch", ":flag_au:", "au.hl2dm.community", 27015, True, 667641710742077460, 0, 0, 0))
servers.append (Server("VirtuousGamers - Germany", ":flag_de:", "vg1.hl2dm.org", 27015, True, 667641755386118154, 0, 0, 0))
servers.append (Server("VirtuousGamers - Illinois", ":flag_us:", "vg3.hl2dm.org", 27015, True, 667641768753496064, 0, 0, 0))
servers.append (Server("VirtuousGamers - Seattle", ":flag_us:", "vg5.hl2dm.org", 27015, True, 667641768753496064, 0, 0, 0))
############################

@client.event
async def on_ready():
    # Set the game that the bot is playing
    await client.change_presence(activity=discord.Game(name=f"Monitoring {numServers} server{'s' if numServers > 1 else ''}"))

    while True:
        for server in servers:
            await broadcast_info(server)

        await asyncio.sleep(auto_refresh_time)

async def broadcast_info(server):
    try:
        queryInfo = a2s.info((server.ip, server.port))
        queryPlayers = a2s.players((server.ip, server.port))
        server_status = 1
        server.updatetime = time.strftime("%H:%M:%S", time.gmtime())
        server.updatedate = time.strftime("%Y-%m-%d")
    except:
        server_status = 0

    #set embed values based on status
    if (server_status == 0):
        server_description = "**~~OFFLINE~~**"
        server_color = 0xDD2E44
        
    else: 
        if(queryInfo.password_protected):
            server_description = "**__ONLINE__** (password protected)\n\n"
            server_color = 0xFDCB58
        else:
            server_description = "**__ONLINE__**\n\n"
            server_color = 0x78B159
            
        server_description += f"**Map:**\u2003{queryInfo.map_name}\n**Mode:**\u2002{queryInfo.game}\n**Players:**\u2002{queryInfo.player_count} / {queryInfo.max_players}"

    # create embed
    embed=discord.Embed(title=f"{server.icon} {server.name if(server.override or server_status == 0) else queryInfo.server_name}", description=server_description, color=server_color)

    if (server_status == 0):
        embed.set_thumbnail(url=f"{url_thumbs}__-offline.jpg")
        if(server.updatetime != 0):
            embed.set_footer(text=f"Last seen online: {server.updatedate} {server.updatetime} UTC")

    else:
        embed.set_thumbnail(url=f"{url_thumbs}{queryInfo.map_name}.jpg")

        # player info fields
        if(queryInfo.player_count):
            server_players = []

            for player in queryPlayers:
                server_players.append (Player(player.name, player.score, int(player.duration)))

            server_players.sort(key=lambda x: x.score, reverse=True) # sort by score

            if(len(server_players[0].name)):
                server_players.sort(key=lambda x: x.score, reverse=True) # sort by score
                
                embed.add_field(name="Player Name", value="\n".join(player.name for player in server_players), inline=True)
                embed.add_field(name="Score", value="\n".join(str(player.score) for player in server_players), inline=True)
                embed.add_field(name="Connected time", value="\n".join(duration(player.duration) for player in server_players), inline=True)

        # connect link [whitespace for width]
        embed.add_field(name="**\u2002**",value = f"**[Connect to server]({url_connect}{server.ip}:{server.port})**⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀", inline=False)

        # set footer
        embed.set_footer(text=f"Updated: {server.updatetime} UTC. Auto-updates every {auto_refresh_time} seconds.")

    # send output
    if(server.message != 0):
        await server.message.delete()

    server.message = await client.get_channel(server.channel).send(embed=embed)

    global botid
    botid = server.message.author.id

    await server.message.add_reaction("🔄")

@client.event
async def on_reaction_add(reaction, user):
    if (user.id != botid and reaction.emoji == "🔄"):
        for server in servers:
            if(server.message == reaction.message):
                await broadcast_info(server)

# Initialise the bot
for server in servers:
    numServers += 1

client.run(bot_token)
