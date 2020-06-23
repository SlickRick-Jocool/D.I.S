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

    def parse(self, path=None):

        """
        Parses a specified insult configuration file for insults.
        We call the InsultParser to handel the reading and interpreting
        of DIS Insult Notation.
        :param path: Path to configuration file. If None, use default.
        :return:
        """

        # Getting insult list:

        raw = self.parser.parse((path if path is not None else self.config))

        # Iterating over raw insult flat list and sorting accordingly:

        for thing in ['flat', 'chain']:

            # Iterate over all relevant insults:

            for word in raw[thing]:

                # Add word to the collection

                self.add_word(word[0], thing, word[1])

    def add_word(self, text, word_type, vulgar=False):

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

            self.safe_insult[word_type].append(text)

        # Add the word to the insult collection:

        self.insults[word_type].append(text)

    def remove_word(self, text, word_type, safe=True):

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

            self.safe_insult[word_type].remove(text)

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

        # Getting start of the argument:

        final = (str(start) if start is not None else self.start) + ' ' + random.choice(collec['flat'])

        # Generating chains:

        for i in range(num - 1):

            # Generate values and combine together into the final insult:

            final = final + ' ' + random.choice(collec['chain']) + ' ' + random.choice(collec['flat'])

        # Return the insult

        return final
