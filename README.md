# Greek New Testament: syntactic parsing for learners

These scripts do some basic syntactic parsing of the Greek New Testament in order to extract segments (ideally, constituents) that are accessible to early learners, using only the constructions they've been exposed to so far.

I originally wanted to use a feature grammar, but the parsing simply wasn't fast enough at the scale I needed (especially with all the non-local dependencies that were required).  Instead, I'm using a dependency grammar, with labels for relations.

The parsing is _not_ intended to be theoretically sophisticated.  My goal is to have a decent representation of the constituent structure for each sentence, for the purpose of automatically extracting meaningful phrases.  The labels are somewhat idiosyncractic.

The morphological parsing of [James Tauber](https://github.com/morphgnt/sblgnt) is used as a base.

The parsed LXX (used to populate some principal parts) comes from [katabiblon.com](https://en.katabiblon.com/us/index.php?text=LXX).
