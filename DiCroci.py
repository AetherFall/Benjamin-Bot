import random
from discord.ext import commands

class DiCroci(commands.Cog, name='DiBot Commands'):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="say", help="Michel please add \n\t[String] <Argument>\n\n" + \
                                  "Répète la chaine entrée en argument. Sauf si cette chaine est \"something\", dans ce cas d'exception, la chaine retournée sera tout autre." + \
                                  "\n\n Exemple:\nMichel please say \"Hello World\"\n",
                 brief="Répète vos mots tel un echo ou bien dis quelque chose de spécial")
    async def rajout(self, ctx, string_arg):
        if string_arg == "something":
            await ctx.send(self.__saySomething())
        else:
            await ctx.send('"' + string_arg + '"')

    @commands.command(name="am", help="Je vous dit si vous êtes ou pas l'un de mes élèves favoris",
                 brief="Êtes-vous mon élève favoris?")
    async def fav(self, ctx, arg1 =None, arg2 =None, arg3 =None, arg4 =None):
        # am I your favorite student?
        if arg1 == "I" and arg2 == "your" and arg3 == "favorite" and arg4 == "student?":
            await ctx.send(self.__favoriteStudent())
        else:
            return

    @commands.command(name="roll", help="Lance un dé")
    async def roll(self, ctx, roll = None):
        if roll is None:
            await ctx.send(random.randint(0,6))
        else:
            try:
                roll = roll.upper().replace("D", "")
                await ctx.send(random.randint(0, int(roll)))
            except (TypeError, ValueError):
                raise Exception("Ce type de dé m'est inconnu. Essayez comme ceci: D12 (Pour un dé à 12 faces)")

##############################################  --METHODS--  ####################################

    #PRIVATE
    def __saySomething(self):
        toSay = {
            0: "Bash.. bash.. bash...",
            1: "kjhbdsf.. eguiv.. eiuvuivui.... \nAi-je expliqué trop rapidement, vous voulez peut-être que je recommence?",
            2: "#!/bin/bash\nypcat passwd > tempfile \ngrep dift2880 < tempfile\nrm tempfile",
            3: "Parce que bien entendu, [gateau] - [patate] = 3",
            4: "Ah! Il y a une erreur dans mon exercice.",
            5: "Bon! Comme tout le monde a échoué cette question à l'examen, je vais l'enlever.",
            6: "Cette session, j'ai décidé de changer le TP, car je le trouvais trop facile. La session dernière, 3 personnes l'ont passé et c'est trop.",
            7: "ArchLinux c'est trop bien, lâchez donc vos Windows et Mac.",
            8: "Clic.. Clic.. Clic.. Clic.. Clic.. Clic.. Clic.. Clic.. Clic.. Clic.. Clic.. Clic.. **Keyboard typing**",
            9: "Au pire, après le cours on ira manger une poutine et je vais t'expliquer tout ça.",
            10: "Shawn? Non, je ne kidnapperais jamais un élève, voyons!",
            11: "Psst.. Les amis! C'est moi Shawn, venez m'aidez, il me garde priso... Mais qu'est-ce que tu fiche ? Lâche l'ordinateur!",
            12: "...À toutes les sauces",
            13: "42... :scream:"
        }
        return toSay[random.randint(0, 13)]

    def __favoriteStudent(self):
        toSay = {
            0: "Non. Tu ne sais même pas faire un réseau local qui fonctionne comme du monde.",
            1: "Non. Tu n'utilises clairement pas ArchLinux...",
            2: "Non. Tu as déjà essayé de me DDOS, je le sais.",
            3: "Non. Tu ne fais pas mes ateliers comme il faut.",
            4: "Non. Je suis certain que vous avez triché dans mon cours de système d'exploitation 2 :face_with_monocle:",
            5: "Oui. Allons manger une poutine après les cours.",
            6: "Oui. Est-ce que tu veux voir mon sous-sol?",
            7: "Oui. Je suis un peu gamer dans mes temps libres, tu veux qu'on s'ajoute sur discord?",
            8: "Oui. Si jamais tu as envie, mon discord c'est: Michel Di Bot#6198",
            9: "Oui. Car toi je sais que tu sais bien ce que fait [Patate] + [Gateau] - 3!"
        }
        return toSay[random.randint(0, 9)]
