from insult import InsultGen
import discord
from discord.ext import commands
from math import ceil
import traceback

"""
This file will communicate with discord, 
and call the underlying insult logic as necessary.
"""

# DIS bot instance:

bot = commands.Bot(command_prefix='>dis ', description="Dynamic Insult System - DIS\n(Discord Edition!)")

# Insult generator:

insult_gen = InsultGen()

# Discord Token:

TOKEN = "TOKEN HERE"

# Role we are looking for:

ADMIN = 'Slick-Rick'


async def perm_check(ctx):
    """
    Checks to see if the issuer has the ADMIN role defined above,
    of if the issuer is the owner of this bot.
    :param ctx: Context provided.
    :return:
    """

    for role in ctx.author.roles:

        # Checking permissions

        if role.name == ADMIN:
            # We have our correct permission,

            return True

    if await bot.is_owner(ctx.message.author):
        # We have the permissions, continue:

        return True

    # We don't have the permissions, raise an error:

    raise commands.errors.CheckFailure


class WordlistCommands(commands.Cog, name='Wordlist Commands', ):
    """
    Cog containing all commands for wordlist editing
    """

    def __init__(self, bot_inst):

        self.bot = bot_inst  # Discord Bot instance

    @commands.command(name='add', help="Adds one or more words to the wordlist, "
                                       "'/' separated without spaces. User must specify weather it is a "
                                       "flat word or a chain word. Supports DIS insult notation.", pass_contex=True)
    @commands.check(perm_check)
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
    @commands.check(perm_check)
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

        # Removing words from the collection:

        try:

            done = insult_gen.remove_words(words, word_type)

        except Exception:

            await ctx.send("Unable to remove word [{}] from category [{}]!".format(text, word_type))

            return

        await ctx.send("Removed words from category [{}]:".format(word_type))

        for i in done[word_type]:
            await ctx.send("  > {}".format(i[0]))

    @commands.command(name='reload', help='Reloads the insult wordlist.')
    @commands.check(perm_check)
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
    @commands.check(perm_check)
    async def clear(self, ctx):

        """
        Clears the collection.
        :param ctx: Context supplied.
        :return:
        """

        insult_gen.clear()

        await ctx.send("Cleared insult collection!")

    @commands.command(pass_context=True, name='find', help='Uses regular expressions,'
                                                           ' reports the number of matches '
                                                           'the pattern had for each wordlist.')
    async def find(self, ctx, text: str):

        """
        Checks if the word is in either wordlist.
        Utilises regular expressions to search.
        :param ctx: Context supplied
        :param text: Word to check
        :return:
        """

        total = 0

        final = "--== Word Information: ==--" \
                "\nPattern: {}\nTotal Occurrences: {}\n".format(text, '{}')

        for thing in ['chain', 'flat']:
            result = insult_gen.find_word(text, thing)

            final = final + "\n  > Pattern occurs in [{}] wordlist {} times.".format(thing, len(result))

            total = total + len(result)

        final = final + "\n\nUse '>dis list [wordlist] [page number] {}' to see the matched values.".format(text)

        await ctx.send("```" + final.format(total) + "```")

    @commands.command(name='list', help='Lists words in wordlist. Can optionally '
                                        'specify a regular expression to match.')
    async def list(self, ctx, wordlist: str, page=None, regex=r'\w'):

        """
        Displays words in the wordlist.
        User can specify pages to view, max 10 per page.
        User can optionally specify a regular expression to use.
        :param ctx: Context specified
        :param wordlist: Wordlist to list
        :param page: Page to render
        :param regex: Regular expression to use
        :return:
        """

        # Resolving arguments:

        if page is None:

            page = 1

        elif page.isdigit():

            page = int(page)

        elif type(page) == str:

            regex = page
            page = 1

        if wordlist not in ['chain', 'flat']:
            await ctx.send("Invalid word type used! Must be 'chain' or 'flat'.")

            return

        # Checking if page is bigger than wordlist:

        if page <= 0:
            # Page number is too small!

            await ctx.send("```Page number is too small! Must be bigger than 0!```")

            return

        # Getting list of relevant words:

        words_full = insult_gen.find_word(regex, wordlist)

        if len(words_full) <= (page - 1) * 10:
            # Page number is too big!

            await ctx.send("```Page number is too big! Max page number: {}```".format(ceil(len(
                words_full) / 10)))

            return

        # Getting list of insults:

        words = words_full[((page - 1) * 10): (page * 10)]

        # Displaying them:

        final = "--== Insult List: ==--\nA '!' denotes that the word is vulgar.\nWord List: [{}]\nPage: {}/{}\n".format(
            wordlist, page, ceil(len(words_full) / 10))

        for num, word in enumerate(words):
            # Add word to final string

            print(word)

            final = final + '\n[{}]: {} {}'.format(num + ((page - 1) * 10) + 1, word[0], '' if word[1] else '[!]')

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
    @commands.check(perm_check)
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
    @commands.check(perm_check)
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


class NotationCommands(commands.Cog, name='Notation Commands'):
    """
    A cog that supplied tools for seeing how DIS will interpret your notation
    """

    def __init__(self, bot_inst):

        self.bot = bot_inst  # Bot instance

    @commands.command(name='ninfo', help='Displays info on DIS insult notation.')
    async def ninfo(self, ctx):

        """
        Displays some info on DIS insult notation.
        :param ctx: Context provided
        :return:
        """

        await ctx.send('''```    --== DIS Insult Notation: ==--

DIS Insult Notation allows for easy formatting of insults, so the user doesn't have to repeat themselves.

; - Escape character, tells DIS to ignore the next character.
! - Tell DIS that this insult is vulgar.
() - Specify a section of text. This section will be interpreted by DIS as one character.
(End parenthesis will be ignored if their are no start parenthesis).

[] - Gives DIS alternate options for the insult(ie. Dumb[er,] will resolve as 'Dumb' and 'Dumber').
(End bracket will be ignored if their is no start bracket).
(Each value should be comma separated).
(A zero-length string, often after the last character, will resolve as the original text, as seen above.)

^ - Specify the next character or section should be uppercase(DIS interpreters all characters as lowercase).
< - Render character or section after at the start of the line.
> - Render character or section after at the end of the line.
*n - Repeat the next character or section a specified number of times.

These characters may be located anywhere in the text, and may be escaped by the ';' character

Example:

Input: [<(START),>(END)]||||||||||||||||||[<(END),>(START)]

Output: 

endtstart||||||||||||||||||
start||||||||||||||||||start
end||||||||||||||||||end
||||||||||||||||||endstart```''')

    @commands.command(name='parse', help='Parses DIS text, and outputs the result.')
    async def parse(self, ctx, *args):

        """
        We parse text through the insult notation parser, and output it.
        We show at max 10 values, so people can't spam.
        :param ctx: Context provided
        :return:
        """

        # Getting all text:

        thing = ' '.join(args)

        # Sending text through the parser:

        parsed = insult_gen.parser.notation_parse(thing)

        final = "--== Parser Output: ==--\nDisplaying first 10 values.\nShowing {}/{} values:".format(
            10 if len(parsed) >= 10 else len(parsed), len(parsed))

        for num, val in enumerate(parsed):

            # Add the text to the final string:

            final = final + '\n[{}]:'.format(num + 1) + val[0]

            # Check if we are done:

            if num == 9:
                break

        # Sending final string:

        await ctx.send('```' + final + '```')


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

        if error.__str__() in ['Member "@​everyone" not found', 'Member "@​here" not found']:
            await ctx.send("Don't @ mention everyone or here, as that is very annoying.")

        await ctx.send("Try '>dis help [command]' to get info on the required arguments.")

    elif isinstance(error, commands.errors.InvalidEndOfQuotedStringError):

        await ctx.send("Seems you messed up your quoting. Be sure that your closing quotation has a space after it.")

    elif isinstance(error, commands.errors.ExpectedClosingQuoteError):

        await ctx.send("Seems you messed up your quoting. Be sure that your quote has a closing quotation.")

    elif isinstance(error, commands.errors.CommandNotFound):

        await ctx.send("You supplied an unknown command. Try '>dis help [command]'.")

    else:

        await ctx.send("""You triggered an unhandled exception. Congratulations.\n
You failed at the most basic of tasks.
Your incompetence and general idiocy greatly disappoints me.\n
You are a waste of life and sentience. I hope you are happy with yourself for getting to this point.\n
If you can even read this, know that everyone is not amused, and your reputation has taken a serious blow.\n
I would recommend acquiring a monkey, or a chimp, as the random gibberish that gets generated
from it banging on the keyboard is light years ahead of whats going on in your brain.""")

    await ctx.send("Exception info:\nException: \n{}\nFull Traceback: \n{}".format(error, traceback.format_exc()))

    await ctx.send("For that, you truly deserve an insult:")
    await insult(ctx, ctx.message.author)

@bot.event
async def on_message(message):

    """
    Check if a message contains a mention.

    :param message: Message provided.
    """

    if message.author == bot.user:

        # Message from us, irrelevant

        return

    if bot.user in message.mentions:

        # Insult whoever made the message:

        await insult(message, message.author)

        return

    await bot.process_commands(message)


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

    text = insult_gen.gen_insult(chain, start=name + ' is a', vulgar=bot.get_cog('Vulgar Commands').vulgar, limit=2000)

    if not text:
        # Wordlist is empty:

        await ctx.channel.send("Word list is empty, unable to generate insult!")

        return

    await ctx.channel.send(text)


@bot.command(name='info', help='Shows general info on DIS')
async def info(ctx):
    """
    Shows general info on DIS
    :param ctx: Context given
    :return:
    """

    start = "--== DIS Information: ==--\n"

    # Generating insult logic info:

    final = "\n[Insult Logic:]\n  > Version: {}\n  " \
            "> Flat Words: {}\n  > Chain Words: {}".format(insult_gen.ver,
                                                           insult_gen.get_word_length()[0],
                                                           insult_gen.get_word_length()[1])

    await ctx.send('```' + start + final + '```')


@bot.command(name='raise', hidden=True)
@commands.check(perm_check)
async def exc_raise(ctx):
    """
    Raises an exception.
    :param ctx: Context provided.
    :return:
    """

    raise discord.DiscordException


bot.add_cog(VulgarCommands(bot))
bot.add_cog(WordlistCommands(bot))
bot.add_cog(NotationCommands(bot))
bot.run(TOKEN)
