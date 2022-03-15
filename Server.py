import asyncio

import pymysql
from datetime import datetime
from enum import Enum
from discord.ext import commands

conn = pymysql.connect(user='root', password='heathcliff', host='127.0.0.1', port=3306, database='examsDB')
bd = conn.cursor()
COMPTDELETE = 60*60

class Type(Enum):
    EXAM = 1
    MINITEST = 2
    TP = 3
    ATELIER = 4


class Cours(Enum):
    MATH = 1
    PROG = 2
    SOUTIEN = 3
    WEB = 4

class Server(commands.Cog, name='Server Commands'):

    def __init__(self, bot):
        self.bot = bot
        self.coursCheck = ""

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            message = "Tu es en train d'oublier des arguments essentiels. Baka!"
        elif isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.CommandOnCooldown):
            message = "Laissez-moi le temps de finir ma correction avant! Réessaye dans {round(error.retry_after, 1)} secondes."
        elif isinstance(error, commands.MissingPermissions):
            message = "Non. Tu n'es pas sudo, tu n'as pas le droit."
        elif isinstance(error, commands.UserInputError):
            message = "Arrête de parler JavaScript et parle-moi en bash!\n\nBy the way, ce que tu viens de m'écrire retourne une erreur de type: UserInputError."
        else:
            message = str(error).replace("Command raised an exception: Exception: ", "")

        await ctx.send(message, delete_after=COMPTDELETE)

    @commands.command(name="add",
                 help="Michel please add \n\t[String] <Type d'examen>\n\t[String] <Code de cours>\n\t[String] <Nom de l'examen/ mot clé>\n\t[String - DATE] <Date de début(\"JJ/MM/YY HH:mm\")>\n\t[String - DATE] <Date de fin(\"JJ/MM/YY HH:mm\")>\n\n" + \
                      "Ajout d'un Examen, TP, Mini-Test, Atelier sur l'horaire des examens en ligne. " + \
                      "\n\n Exemple:\nMichel please add Examen 420-C46 \"Intra Prog C#\" \"03/02/22 14:40\" \"03/02/22 16:30\"" + \
                      " \n\n\t-- typeExam --\n" + \
                      "\tExamen\n" + \
                      "\tMini-test\n" + \
                      "\tTP\n" + \
                      "\tAtelier\n\n" + \
                      "\t-- codeCours --\n" + \
                      "\t201-T45  | Géométrie vectorielle appliquée à l'informatique\n" + \
                      "\t420-C46  | Conception et développement orientés objet\n" + \
                      "\t420-M43  | Soutien technique\n" + \
                      "\t420-N46  | Conception et développement d'applications Web\n\n" + \
                      "Les dates doivent être écrites sous ce format:\n" + \
                      "[\"JJ/MM/AA HH:mm\"]\n" + \
                      "Les symboles (/, :, \" et [SPACE]) ne sont pas la pour faire jolie.\n\n\n" + \
                      "Tout écart de conduite entrainera la note de 0, mais comme je suis gentil je vous laisse un nombre illimité d'essais.",
                 brief="Ajout d'examen à la Base de données")
    async def ajout(self, ctx, typeExam, codeCours, nomExam, date, dateRemise):
        examenType = self.__typeDeDevoir(typeExam)
        cours = self.__coursType(codeCours)

        # Cas d'exception
        if examenType is None:
            raise Exception("Ehm.. Excuse-moi? Mais quel est ce terme? Je ne le connais pas. [" + typeExam + "]?")
        if cours is None:
            raise Exception(
                typeExam + "... Ce n’est pas un cours que je connais. Recommence, mais ce coup-ci, avec un cours que je connais.")

        try:
            date = datetime.strptime(date, '%d/%m/%y %H:%M')
            dateRemise = datetime.strptime(dateRemise, '%d/%m/%y %H:%M')

        except (ValueError, TypeError):
            raise Exception("Pardon? Les dates que tu m'as fournies sont invalides.")

        dateToShow = (dateRemise.strftime("à``` %H:%M```"), dateRemise.strftime("```%A %d %B à %H:%M```"))[
            examenType == Type.ATELIER or examenType == Type.TP]

        self.__addToBD(examenType, cours, nomExam, date, dateRemise)
        await ctx.message.channel.send(
            "D'accord, j'ajoute un " + typeExam + " de " + self.coursCheck + " pour la date suivante: ```" + date.strftime(
                "%A le %d %B à %H:%M") + "``` et prendra fin " + dateToShow)


    @commands.command(name="delay", help="", brief="Reporter un examen")
    async def delay(self, ctx, typeExam, codeCours, date, newDate, newRemise):
        cours = self.__coursType(codeCours)
        examenType = self.__typeDeDevoir(typeExam)

        # Cas d'exceptions
        if examenType is None:
            raise Exception("Ehm.. Excuse-moi? Mais quel est ce terme? Je ne le connais pas. [" + typeExam + "]")
        if cours is None:
            raise Exception(
                codeCours + "... Ce n’est pas un cours que je connais. Recommence, mais ce coup-ci, avec un cours que je connais.")

        try:
            dateEnCours = datetime.strptime(date, '%d/%m/%y')
            delayDate = datetime.strptime(newDate, '%d/%m/%y %H:%M')
            dateRemise = datetime.strptime(newRemise, '%d/%m/%y %H:%M')
        except (ValueError, TypeError):
            raise Exception("Pardon? Les dates que tu m'as fournies sont invalides.")

        affichage = (dateRemise.strftime("%A le %d %B à %H:%M"), dateRemise.strftime("%H:%M"))[
            dateRemise.day == delayDate.day and dateRemise.month == delayDate.month]

        self.__mod(examenType, cours, dateEnCours, delayDate, dateRemise)
        await ctx.message.channel.send(
            "D'accord, je modifie ce qui était programmé pour le cours: " + self.coursCheck + ", du ```" + dateEnCours.strftime(
                "%A le %d %B") + "``` pour " + "```" + delayDate.strftime(
                "%A le %d %B à %H:%M") + "```" + "La fin de cet évènement est programmée pour: ```" + affichage + "```")

    @commands.command(name="delete", help="", brief="Reporter un examen")
    async def delete(self, ctx, typeExam, codeCours, date):
        cours = self.__coursType(codeCours)
        examenType = self.__typeDeDevoir(typeExam)

        # Cas d'exceptions
        if examenType is None:
            raise Exception("Ehm.. Excuse-moi? Mais quel est ce terme? Je ne le connais pas. [" + typeExam + "]")
        if cours is None:
            raise Exception(codeCours + "... Ce n’est pas un cours que je connais. Recommence, mais ce coup-ci, avec un cours que je connais.")

        try:
            dateEnCours = datetime.strptime(date, '%d/%m/%y')
        except (ValueError, TypeError):
            raise Exception("Pardon? Les dates que tu m'as fournies sont invalides.")

        channel = ctx.message.channel
        await channel.send('Souhaitez-vous vraiment supprimer cet évènement?\n👍 / 👎')

        def check(reaction, user):
            return user == ctx.message.author and (str(reaction.emoji) == '👍' or str(reaction.emoji) == '👎')

        try:
            reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.message.channel.send("Bon! Vu que tu ne t'es pas décidé à temps, j'annule l'opération.")
        else:
            if str(reaction.emoji) == '👍':
                self.__del(examenType, cours, dateEnCours)
                await ctx.message.channel.send(
                    "D'accord, je supprime cet évènement: ```" + typeExam + ' - ' + self.coursCheck + ' - ' + dateEnCours.strftime(
                    "%A le %d %B") + "```")
            else:
                await ctx.message.channel.send("D'accord, j'annule l'opération.")





##############################################  --METHODS--  ####################################

    def __addToBD(self, examenType, cours, nomExam, date, dateRemise):
        bd.execute(
            "INSERT INTO registre (registreCoursId, registreTypeId, registreNom, registreDate, registreHeureDebut, registreDateFin, registreHeureFin) " +\
            "VALUES('" + str(cours.value) + "', '" + str(examenType.value) + "', '" + nomExam + "', '" +\
            date.strftime("%Y-%m-%d") + "', '" + date.strftime("%H:%M") + "', '" +\
            dateRemise.strftime("%Y-%m-%d") + "', '" + dateRemise.strftime("%H:%M") + "');")

        print(str(bd.rowcount) + " details inserted")
        conn.commit()

    def __mod(self, examenType, cours, date, newDate, newRemise):
        bd.execute("UPDATE registre SET registreDate = '"+ newDate.strftime("%Y-%m-%d") +\
                   "', registreHeureDebut ='"+ newDate.strftime("%H:%M") +\
                   "', registreDateFin ='"+ newRemise.strftime("%Y-%m-%d") +\
                   "', registreHeureFin ='" + newRemise.strftime("%H:%M") +\
                   "' WHERE registreDate = '"+ date.strftime("%Y-%m-%d") +\
                   "' and registreCoursId = '"+ str(cours.value) +\
                   "' and registreTypeId = '"+ str(examenType.value) +"';")

        print(str(bd.rowcount) + " detail updated")
        conn.commit()

    def __del(self, examenType, cours, dateEnCours):
        bd.execute("DELETE FROM registre WHERE registreTypeId='" + str(examenType.value) + "' and registreCoursId='" + str(cours.value) + "' and registreDate='"+ dateEnCours.strftime("%Y-%m-%d") +"';")

        print(str(bd.rowcount) + " detail deleted")
        conn.commit()

    # TYPE EXAMEN
    def __typeDeDevoir(self, typeExam):
        if typeExam.upper() == 'EXAMEN' or typeExam.upper() == 'EXAM':
            return Type.EXAM
        if typeExam.upper() == 'MINI-TEST' or typeExam.upper() == 'MINITEST' or typeExam.upper() == 'TEST':
            return Type.MINITEST
        if typeExam.upper() == 'TP' or typeExam.upper() == 'TRAVAIL-PRATIQUE' or typeExam.upper() == 'TRAVAIL PRATIQUE':
            return Type.TP
        if typeExam.upper() == 'ATELIER' or typeExam.upper() == 'EXERCICE':
            return Type.ATELIER
        return None

    # CODE COURS
    def __coursType(self, codeCours):
        if codeCours.upper() == '201-T45' or codeCours.upper() == '201-T45-JO' or codeCours.upper() == 'T45':
            self.coursCheck = "Géométrie vectorielle appliquée à l'informatique"
            return Cours.MATH
        if codeCours.upper() == '420-C46' or codeCours.upper() == '420-C46-JO' or codeCours.upper() == 'C46':
            self.coursCheck = "Conception et développement orientés objet"
            return Cours.PROG
        if codeCours.upper() == '420-M43' or codeCours.upper() == '420-M43-JO' or codeCours.upper() == 'M43':
            self.coursCheck = "Soutien technique"
            return Cours.SOUTIEN
        if codeCours.upper() == '420-N46' or codeCours.upper() == '420-N46-JO' or codeCours.upper() == 'N46':
            self.coursCheck = "Conception et développement d'applications Web"
            return Cours.WEB
        return None