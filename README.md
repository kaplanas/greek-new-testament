# Greek New Testament: syntactic parsing for learners

These scripts do some basic syntactic parsing of the Greek New Testament in order to extract segments (ideally, constituents) that are accessible to early learners, using only the constructions they've been exposed to so far.

I originally wanted to use a feature grammar, but the parsing simply wasn't fast enough at the scale I needed (especially with all the non-local dependencies that were required).  Instead, I'm using a dependency grammar, with labels for relations.

I modified `nltk`'s `DependencyGrammar` class (and some related classes) to allow for some basic feature parsing.  This lets me write rules like "an indicative verb can have a subject that is a noun with the same person and number" instead of having to list every lexical item separately.  On the other hand, the lexicon contains a mix of true lexical information (e.g., which verbs can take an accusative argument) and accidents of the corpus (e.g., which nouns happen to be conjoined, which lets me write more specific rules that keep the number of possible parses under control).

The parsing is _not_ intended to be theoretically sophisticated.  My goal is to have a decent representation of the constituent structure for each sentence, for the purpose of automatically extracting meaningful phrases.  The labels are somewhat idiosyncractic, and drastically oversimplified (for example, I haven't distinguished between PPs that are arguments vs. modifiers).

The morphological parsing of [James Tauber](https://github.com/morphgnt/sblgnt) is used as a base.

The parsed LXX (used to populate some principal parts) comes from [katabiblon.com](https://en.katabiblon.com/us/index.php?text=LXX).
