from insult import InsultGen
import discord
from discord.ext import commands
from math import ceil

"""
This file will communicate with discord, 
and call the underlying insult logic as necessary.
"""

# DIS bot instance:

bot = commands.Bot(command_prefix='>dis ')

# Insult generator:

insult_gen = InsultGen()

# Discord Token:

TOKEN = 'TOKEN'

# Role we are looking for:

ADMIN = 'Slick-Rick'


class WordlistCommands(commands.Cog, name='Wordlist Commands', ):

    """
    Cog containing all commands for wordlist editing
    """

    def __init__(self, bot_inst):

        self.bot = bot_inst  # Discord Bot instance

    @commands.command(name='add', help="Adds one or more words to the wordlist, "
                      "'/' separated without spaces. User must specify weather it is a "
                      "flat word or a chain word. Supports DIS insult notation.", pass_contex=True)
    @commands.has_role(ADMIN)
    async def add(self, ctx, word_type: str, text: str):

        """
        Adds one or more words to the wordlist.
        :param ctx: Context supplied
        :param word_type: Specifies the type of word('chain or flat')
        :param text: Word to add
        :return:
        """

        # Checking arguments:

        if word_type not in ['chain', 'flat']:

            await ctx.send("Invalid word type used! Must be 'chain' or 'flat'.")

            return

        # Splitting words:

        words = text.split('/')

        # Adding words to the collection:

        done = insult_gen.add_words(words, word_type)

        await ctx.send("Added words to category [{}]:".format(word_type))

        for i in done[word_type]:
            await ctx.send("  > {}".format(i[0]))

    @commands.command(pass_context=True, name='remove', help="Removes one or more words to the wordlist, "
                      "'/' separated without spaces. "
                      "User must specify weather it is a flat word or a chain word. "
                      "Supports DIS insult notation.")
    @commands.has_role(ADMIN)
    async def remove(self, ctx, word_type: str, text: str):

        """
        Removes one or more words from the wordlist.
        Words will be passed through the notation parser.
        :param ctx: Context provided
        :param word_type: Type of word to remove
        :param text: Word to remove
        :return:
        """

        # Checking arguments:

        if word_type not in ['chain', 'flat']:

            await ctx.send("Invalid word type used! Must be 'chain' or 'flat'.")

            return

        # Splitting words:

        words = text.split('/')

        # Adding words to the collection:

        done = insult_gen.remove_words(words, word_type)

        await ctx.send("Removed words from category [{}]:".format(word_type))

        for i in done[word_type]:
            await ctx.send("  > {}".format(i[0]))

    @commands.command(name='reload', help='Reloads the insult wordlist.')
    async def reload(self, ctx):

        """
        Reloads the insult wordlist.
        :param ctx: Context supplied.
        :return:
        """

        await ctx.send("Reloading insult wordlist...")

        insult_gen.parse()

        await ctx.send("Reloaded insult wordlist!")

    @commands.command(name='clear', help="Clears all words from the collection.")
    @commands.has_role(ADMIN)
    async def clear(self, ctx):

        """
        Clears the collection.
        :param ctx: Context supplied.
        :return:
        """

        insult_gen.clear()

        await ctx.send("Cleared insult collection!")

    @commands.command(pass_context=True, name='find', help='Checks if the word is in either wordlist.')
    async def find(self, ctx, text: str):

        """
        Checks if the word is in either wordlist.
        :param ctx: Context supplied
        :param text: Word to check
        :return:
        """

        # Checking if the word is in chain words:

        chain, chain_safe = insult_gen.check_word(text, 'chain')

        # Checking if word is in flat words:

        flat, flat_safe = insult_gen.check_word(text, 'flat')

        final = "--== Word Information: ==--\nWord: {}\n".format(text)

        if chain:
            final = final + "\n  > Word is present in 'chain' wordlist, and {} vulgar.".format("is not" if chain_safe
                                                                                               else "is")

        if flat:
            final = final + "\n  > Word is present in 'flat' wordlist, and {} vulgar.".format("is not" if flat_safe
                                                                                              else "is")

        if not flat and not chain:
            final = final + "\n   > Word is not present in any wordlist."

        await ctx.send("```" + final + "```")

    @commands.command(name='list', help='Lists words in wordlist.')
    async def list(self, ctx, wordlist: str, page=1):

        """
        Displays words in the wordlist.
        User can specify pages to view, max 10 per page.
        :param ctx: Context specified
        :param wordlist: Wordlist to list
        :param page: Page to render
        :return:
        """

        if wordlist not in ['chain', 'flat']:

            await ctx.send("Invalid word type used! Must be 'chain' or 'flat'.")

            return

        # Checking if page is bigger than wordlist:

        if page <= 0:
            # Page number is too small!

            await ctx.send("```Page number is too small! Must be bigger than 0!```")

            return

        if len(insult_gen.insults[wordlist]) <= (page - 1) * 10:
            # Page number is too big!

            await ctx.send("```Page number is too big! Max page number: {}```".format(ceil(len(
                insult_gen.insults[wordlist]) / 10)))

            return

        # Getting list of insults:

        words = insult_gen.insults[wordlist][((page - 1) * 10): (page * 10)]

        # Displaying them:

        final = "--== Insult List: ==--\nA '!' denotes that the word is vulgar.\nWord List: [{}]\nPage: {}/{}\n".format(
            wordlist, page, ceil(len(insult_gen.insults[wordlist]) / 10))

        for num, word in enumerate(words):

            # Find out if it is in the safewords:

            end = '[!]'

            if word in insult_gen.safe_insult[wordlist]:
                # Word is in wordlist:

                end = ''

            final = final + '\n[{}]: {} {}'.format(num + ((page - 1) * 10) + 1, word, end)

        await ctx.send("```" + final + "```")

    @commands.command(name='all', help='Send wordlist to channel.')
    async def all(self, ctx):

        """
        Sends the insult wordlist as a file.
        :param ctx: Context provided.
        :return:
        """

        await ctx.send("Sending DIS insult wordlist, please wait...")

        # Sending wordlist:

        await ctx.send(file=discord.File(insult_gen.config, filename="all_insults.txt"))

        await ctx.send("Wordlist sent!")


class VulgarCommands(commands.Cog, name='Vulgar Commands'):

    """
    Cog that controls weather DIS should use vulgarity
    """

    def __init__(self, bot):

        self.bot = bot  # Discord bot instance
        self.vulgar = True  # Weather we should use vulgarity

    @commands.command(name='enable', help='Enables vulgarity')
    @commands.has_role(ADMIN)
    async def enable(self, ctx):

        """
        Enables vulgarity
        :param ctx: Context given
        :return:
        """

        if self.vulgar:
            # Vulgarity already enabled, do nothing!

            await ctx.send('Vulgarity is already enabled!')

            return

        # Enabling vulgarity

        self.vulgar = True

        await ctx.send("Vulgarity Enabled!")

    @commands.command(name='disable', help='Disables vulgarity')
    @commands.has_role(ADMIN)
    async def disable(self, ctx):

        """
        Enables vulgarity
        :param ctx: Context given
        :return:
        """

        if not self.vulgar:
            # Vulgarity already disabled, do nothing!

            await ctx.send('Vulgarity is already disabled!')

        self.vulgar = False

        await ctx.send("Vulgarity disabled!")

    @commands.command(name='check', help='Checks vulgarity value')
    async def check(self, ctx):

        """
        Checks vulgarity and reports it
        :param ctx: Context given
        :return:
        """

        await ctx.send("Vulgarity is: [{}]".format("Enabled" if self.vulgar else "Disabled"))


@bot.event
async def on_ready():

    print("DIS Has connected to discord!")


@bot.event
async def on_command_error(ctx, error):

    """
    Handles a command error
    :param ctx: Given context
    :param error: Error given
    :return:
    """

    if isinstance(error, commands.errors.CheckFailure):

        await ctx.send("You don't have the correct role for this command.")

    elif isinstance(error, commands.errors.MissingRequiredArgument):

        await ctx.send("You are missing a required argument. Try '>dis help [command]'.")

    elif isinstance(error, commands.errors.BadArgument):

        await ctx.send("You supplied a bad argument.")
        await ctx.send("Don't @ 'everyone' or 'here', as that is very annoying.")

    else:

        await ctx.send("""You triggered an unhandled exception. Congratulations.\n
You failed at the most basic of tasks.
Your incompetence and general idiocy greatly disappoints me.\n
You are a waste of life and sentience. I hope you are happy with yourself for getting to this point.\n
If you can even read this, know that everyone is not amused, and your reputation has taken a serious blow.\n
I would recommend acquiring a monkey, or a chimp, as the random gibberish that gets generated
from it banging on the keyboard is light years ahead of whats going on in your brain.""")

    await ctx.send("For that, you truly deserve an insult:")
    await insult(ctx, ctx.message.author)


@bot.command(name='insult', help='Insults a particular user.')
async def insult(ctx, user: discord.Member, chain=3):

    """
    DIS a user. User must @mention a user, and can optionally supply chains
    :param ctx: Context given
    :param user: User to insult
    :param chain: Number of chains to use
    :return:
    """

    if user == bot.user:

        # We don't insult ourselves, insult the issuer instead!

        name = ctx.message.author.mention

    else:

        # Getting name to insult:

        name = user.mention

    text = insult_gen.gen_insult(chain, start=name + ' is a', vulgar=bot.get_cog('Vulgar Commands').vulgar)

    if not text:

        # Wordlist is empty:

        await ctx.send("Word list is empty, unable to generate insult!")

        return

    await ctx.send(text)


@bot.command(name='raise', hidden=True)
@commands.has_role(ADMIN)
async def exc_raise(ctx):

    """
    Raises an exception.
    :param ctx: Context provided.
    :return:
    """

    raise discord.DiscordException


bot.add_cog(VulgarCommands(bot))
bot.add_cog(WordlistCommands(bot))
bot.run(TOKEN)
