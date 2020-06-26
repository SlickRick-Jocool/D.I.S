import random
from fileutils import InsultParser

"""
This file will contain all insult logic for DIS.
Ideally, the insults will be generated with minimal configuration and parameters,
so the API implementation can easily get an insult.

Insults will be generated as so:

[START] + [FLAT WORD] + ([Chain Word] + [Flat Word]) * n - 1

Chain word = Word that "chains" statements together - and, is, ect.
Flat word = Statement that is the brunt of the insult - bad, trash, terrible, ect.
Start Word = Word that can effectively start off the sequence.
n = Number which specifies how many "chains" the insult will have.

Chase is bad - 1 chain
Chase is bad and trash - 2 chains

Pros:

Simple algorithm
Low computing power
Scalability - Add as many words as we want

Cons:

Might be too simple
Statements that make little sense
Insults that may lack emphasis - weak insults
"""


class InsultGen:

    """
    InsultGen handles all insult logic, and allows for generating, adding, removing,
    and parsing the config(s) file for insults.
    """

    CHAIN = 'chain'
    FLAT = 'flat'

    def __init__(self, config='insults.txt', start="You are"):

        self.parser = InsultParser()
        self.insults = {'flat': [], 'chain': []}  # Dictionary of insult words
        self.safe_insult = {'flat': [], 'chain': []}  # Dictionary for non-vulgar insults
        self.config = config  # Path to default insult file
        self.start = start  # Default phrase to start the insult.

        # Parsing over insult file:

        self.parse()

    def clear(self):

        """
        Cleared the internal collection of inputs
        :return:
        """

        self.insults = {'flat': [], 'chain': []}
        self.safe_insult = {'flat': [], 'chain': []}

    def parse(self, path=None):

        """
        Parses a specified insult configuration file for insults.
        We call the InsultParser to handel the reading and interpreting
        of DIS Insult Notation.
        :param path: Path to configuration file. If None, use default.
        :return:
        """

        # Clearing internal values:

        self.insults = {'flat': [], 'chain': []}
        self.safe_insult = {'flat': [], 'chain': []}

        # Getting insult list:

        raw = self.parser.parse((path if path is not None else self.config))

        # Parsing over the dictionary and adding relevant words:

        self._parse_dict(raw)

    def _parse_dict(self, raw, remove=False):

        """
        Parses a specified dictionary and adds the words as they are found.
        :param raw: Dictionary to parse.
        :param remove: Value determining if we should remove words
        :return:
        """

        # Iterating over RAW insult list and sorting accordingly:

        for thing in ['flat', 'chain']:

            # Iterate over all relevant insults:

            for word in raw[thing]:

                if not remove:

                    # Add word to collection:

                    self._add_word(word[0], thing, word[1])

                    continue

                else:

                    self._remove_word(word[0], thing, word[1])

    def check_word(self, word, word_type):

        """
        Checks if a word is in the collection
        :param word: Word to check
        :param word_type: Type of word to check
        :return:
        """

        # Check if word is in the master list:

        insult = word in self.insults[word_type]

        # Check if word is in safe list:

        safe = word in self.safe_insult[word_type]

        return insult, safe

    def add_words(self, words, word_type):

        """
        Allows for the addition of one or more words.
        Sends the words through the DIS notation parser.
        :param words: Words to add, can be string or list.
        :param word_type: Type of words
        :return:
        """

        out = {'chain': [], 'flat': []}

        if type(words) == str:

            # Convert into a list:

            words = [words]

        # Working with a list, handel it as such:

        for word in words:

            # Send the word through the parser:

            out[word_type] = out[word_type] + self.parser.notation_parse(word)

        # Parse raw words and add them to dictionary:

        self._parse_dict(out)

        return out

    def remove_words(self, words, word_type):

        """
        Allows for the removal of one or more words.
        Sends the words through the DIS notation parser.
        :param words: Words to add, can be string or list
        :param word_type: Type of words to add
        :return:
        """

        out = {'chain': [], 'flat': []}

        if type(words) == str:

            # Convert into list:

            words = [words]

        # Working with a list:

        for word in words:

            # Send word through the parser

            out[word_type] = out[word_type] + self.parser.notation_parse(word)

        # Parse raw words and remove them from the dictionary

        self._parse_dict(out, remove=True)

        return out

    def _add_word(self, text, word_type, vulgar=False):

        """
        Adds a word(Or a statement) to the internal collection.
        These words are not persistent and will be reset on the next runtime.
        :param text: Word(s) to add.
        :param word_type: Specifies which word it is, 'chain' or 'flat'
        :param vulgar: Boolean determining if he word is vulgar
        :return:
        """

        if not vulgar:

            # Word is not vulgar, add it to the safe words:

            if text in self.safe_insult[word_type]:

                # Already have to word registered, do nothing.

                return

            self.safe_insult[word_type].append(text)

        if text in self.insults[word_type]:

            # Already have word registered, do nothing

            return

        # Add the word to the insult collection:

        self.insults[word_type].append(text)

    def _remove_word(self, text, word_type, safe=True):

        """
        Removes a word from the internal collection.
        :param text: Text to remove(Can also be the index of a word)
        :param word_type: Type of word to remove, 'chain' or 'flat'
        :param safe: Will attempt to remove the word from the safe wordlist.
        :return: True if success, False if Failure
        """

        if type(text) == int:

            # Working with an integer, resolve this value:

            text = self.insults[word_type][text]

        # Remove the text from the main insult list:

        self.insults[word_type].remove(text)

        if safe:

            # Attempt to remove form the safe word list:

            try:

                self.safe_insult[word_type].remove(text)

            except Exception:

                # Word not in safe list, move on

                pass

    def gen_insult(self, num, start=None, vulgar=False):

        """
        Generates an insult based on the internal collection.
        User can define how many 'chains' the insult has,
        as well as the start of the insult, as well as if vulgar words should be used.
        :param num: Number of chains the insult has
        :param start: Start text. If none, resort to default.
        :param vulgar: Boolean determining if we should use vulgar insults.
        :return: Insult in string format
        """

        collec = (self.insults if vulgar else self.safe_insult)

        if collec == {'flat': [], 'chain': []}:

            # Empty wordlist, return false

            return False

        # Getting start of the argument:

        final = (str(start) if start is not None else self.start) + ' ' + random.choice(collec['flat'])

        # Generating chains:

        for i in range(num - 1):

            # Generate values and combine together into the final insult:

            final = final + ' ' + random.choice(collec['chain']) + ' ' + random.choice(collec['flat'])

        # Return the insult

        return final
