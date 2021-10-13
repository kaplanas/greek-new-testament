# Greek New Testament: syntactic parsing for learners

These scripts do some basic syntactic parsing of the Greek New Testament in order to extract segments (ideally, constituents) that are accessible to early learners, using only the constructions they've been exposed to so far.

The parsing is _not_ intended to be theoretically sound.  My goal is to have a decent representation of the constituent structure (not necessarily the right labels or the right number of functional heads) for each sentence, with a minimum of ambiguity.  I particularly want to avoid ambiguity with no associated semantic distinction.  This results in some questionable representations (e.g., PPs are always adjuncts and never arguments; some word order alternatives are represented with duplicated rules rather than movement).  Also, because nltk feature grammars don't allow "not" or "or" logic within feature structures, there's a massive amount of duplication in the syntactic rules.

The morphological parsing of [James Tauber](https://github.com/morphgnt/sblgnt) is used as a base.

The parsed LXX (used to populate some principal parts) comes from [katabiblon.com](https://en.katabiblon.com/us/index.php?text=LXX).
