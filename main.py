from discord.ext import commands
import DiCroci
import Server

#CONSTANTES
TOKEN = ''
COMMAND_INIT = 'Michel please '

bot = commands.Bot(command_prefix=COMMAND_INIT)

bot.add_cog(DiCroci.DiCroci(bot))
bot.add_cog(Server.Server(bot))

@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))

bot.run(TOKEN)