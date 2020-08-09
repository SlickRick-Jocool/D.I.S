
"""
This file will contain all utility functions for pulling
insults(and maybe default values?) from configuration files located somewhere.

This increases the modularity and usability of ChaseBot,
and allows for users to easily add content to DIS.

These configuration files will contain lists of chain words and flat words
to be used for generating insults.

They will support commenting, insult notation, sections, and even config options later on.

Content *MUST* be restricted to one line. Comments can be multi-lined, but they will have to append a
comment character(Customisable, but most likely '#')

--== DIS Insult Notation: ==--

DIS Insult Notation allows for easy formatting of insults, so the user dosen't have to repeat themselves.

; - Escape character, tells DIS to ignore the next character
! - Tell DIS that this insult is vulgar.
() - Specify a section of text. This section will be interpreted by DIS as one character.
(End parenthesis will be escaped if the first one is escaped)
(All characters in parenthesis are automatically escaped.)
[] - Gives DIS alternate options for the insult(ie. Dumb[er] will resolve as 'Dumb' and 'Dumber')
(End bracket will be escaped if first one is escaped)
(Each value should be comma separated)
^ - Specify the next character or section should be uppercase(DIS interpreters all characters as lowercase)
< - Render character or section after at the start of the line
> - Render character or section after at the end of the line
*n - Repeat the next character or section a specified number of times

These characters may be located anywhere in the text, and may be escaped by the ';' character
"""


class InsultParser:

    """
    The aforementioned insult parser.
    You can see more information about it above.
    """

    def __init__(self):

        self.comment = '#'  # Comment character, denotes text we don't care about
        self.reader = None  # File object we use for reading.
        self.start_flat = '------flat words:------'  # Header for flat words
        self.start_chain = '------chain words:------'  # Header for chain words
        self.stop = '------end section:------'  # Header for end section

    def parse(self, path):

        """
        Parses over the insults and returns a dictionary mapping chainwords and flatwords.
        :param path: Path to insult file
        :return: Dictionary wor words.
        """

        # Open a file object on the path specified:

        flat = []
        chain = []
        selected = None

        with open(path, mode='r') as self.reader:

            # We now iterate over the text:

            for line in self.reader:

                # Removing newlines and other junk

                line = line.rstrip("\n")
                line = line.replace("\n", '')
                line = line.lower()

                if line == '' or line[0] == self.comment:

                    # We don't care about this, ignore it:

                    continue

                if line == self.start_flat:

                    # Started flat word section, add flat words to list:

                    selected = 1

                    continue

                if line == self.start_chain:

                    # Started chain word section, add flat words to list:

                    selected = 2

                    continue

                if line == self.stop:

                    # End of section:

                    selected = None

                    continue

                # Add word to relevant list, if we are in a section:

                if selected is not None:

                    if selected == 1:

                        # Add to flat wordlist:

                        flat = flat + self.notation_parse(line)

                    else:

                        # Add to chain wordlist

                        chain = chain + self.notation_parse(line)

                    continue

            # End of parsing, return dictionary of words:

            return {'flat': flat, 'chain': chain}

    def _split_statement(self, text):

        """
        Splits text up into characters or sections. Makes the parsing process easier.
        We also interpret the content in parenthesis, as they should be processed first.
        :param text: Text to format
        :return: List of split text
        """

        index = 0
        final = []

        # While loop to iterate over text

        while index < len(text):

            char = text[index]

            if char == '(' and text[index-1] != ';':

                # Start of a section, find the end

                end = text.find(')', index)

                if end == -1:

                    raise(Exception("No terminating parenthesis! Add ')' or escape '('!"))

                # Send groups through notation parser so they can be interpreted: first

                final.append(''.join(self.notation_parse(text[index+1:end], find_vulg=False)))

                index = end + 1

                continue

            # Just append the character to the list

            final.append(char)

            # Increment the index

            index = index + 1

        # Done iterating, return

        return final

    def _statement_expand(self, text) -> list:

        """
        Expands statements based on brackets. Finds all possible combinations for statement.
        We implement some recursion so we can get all the possible combos.
        :param text: Text to be split.
        :return: List of split statements
        """

        # Finding first instance of open bracket.

        start = text.find('[')

        if start != -1 and text[start-1] != ';':

            # We have a bracket, find the end bracket:

            stop = text.find(']', start)

            if stop == -1:

                raise(Exception("No terminating bracket! Add ']' or escape '['!"))

            # Split up text in the bracket:

            split = text[start+1:stop].split(',')

            # Add split text to final:

            done = list(text[:start] + x + text[stop+1:] for x in split)
            final = []

            for i in done:

                final = final + self._statement_expand(i)

            return final

        elif start != -1 and text[start-1] == ';':

            # Get expansion for the rest of the text:

            new = self._statement_expand(text[start+1:])
            final = []

            for i in new:

                final.append(text[:start+1] + i)

            return final

        return [text]

    def notation_parse(self, text, find_vulg=True):

        """
        Parses notation characters and generates new text based off of it.
        :param text: Text to be formatted
        :param find_vulg: Value determining if we should find vulgarity
        :return: Formatted text in a list
        """

        text = text.lower()

        # We first expand the text:

        exp = self._statement_expand(text)
        ret = []

        for state in exp:

            # We now split up the statement into list form:

            split = self._split_statement(state)

            # Now we iterate over each character to do our format operations:

            index = 0  # Index of pointer
            final = []  # Final collection of text
            end = []  # Text to add to the end of the statement
            vulg = False  # Value determining if statement is vulgar

            while index < len(split):

                char = split[index]

                if char == ';':

                    # Next character is to be added to the collection:

                    final.append(split[index+1])

                    index = index + 2

                    continue

                elif char == '!' and find_vulg:

                    # Insult is vulgar, do something

                    vulg = True

                    index = index + 1

                    continue

                elif char == '^':

                    # Next character should be uppercase

                    final.append(split[index+1].upper())

                    index = index + 2

                    continue

                elif char == '<' or char == '>':

                    # Next character should be moved to the start/end of the statement:

                    move = split.pop(index + 1)

                    if char == '<':

                        final.insert(0, move)

                    else:

                        end.append(move)

                    index = index + 1

                    continue

                elif char == '*':

                    # Repeat the next character a specified number of times:

                    num = split[index+1]

                    try:

                        num = int(num)

                    except:

                        raise Exception("No number after '*' char! Must be in form '*3' or '*(123)!")

                    final.append(split[index+2] * num)

                    index = index + 3

                    continue

                else:

                    # Add character to final:

                    final.append(char)

                    index = index + 1

                    continue

            # Merging final + end statements

            final = final + end

            if find_vulg:

                ret.append([''.join(final), vulg])

            else:

                ret.append(''.join(final))

            continue

        return ret
