import random

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

CHAIN = ['and a', 'fucking', 'shitting', 'fricking', 'damning', 'trashing', 'bitching']
FLAT = ['fuck', 'fucker', 'brick', 'trash', 'crap', 'terrible', 'shit', 'dick', 'asshole', 'ass',
        'bastard', 'bugger', 'rubbish', 'bitch', 'sucker']
START = ['terrible', 'damn', 'dick', 'shit', 'bitch', 'bugger', 'bastard', 'brick', 'trash', 'crap']


def gen_insult(num, start='Chase is a'):

    """
    Generates an insult based on the internal collection of words.
    User can define how many "chains" the insult has.
    :param num: Number of chains the insult has
    :param start: String to start the sequence
    :return: Insult in string form.
    """

    # Lopping a specified amount of times:

    final = start + ' ' + random.choice(START)

    num = num - 1

    for i in range(num):

        # Randomly select a chain word:

        chain = random.choice(CHAIN)

        # Randomly select Flat word:

        flat = random.choice(FLAT)

        # Combine together into the final insult:

        final = final + ' ' + chain + ' ' + flat

    # Return the insult

    return final
