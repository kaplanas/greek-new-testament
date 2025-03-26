# Greek New Testament: Excerpts for Learners

These scripts extract contiguous strings from the Greek New Testament and writes them to a database.  The goal is to make it possible to query intact segments that are accessible to early learners, using only the constructions they've been exposed to so far.

I use syntactic parses to identify strings that are (more or less) syntactically coherent.  The [Global Bible Initiative trees of the SBL New Testament](https://github.com/biblicalhumanities/greek-new-testament/tree/master) are used as a starting point; these scripts convert those trees to a dependency representation, make some modifications, and decorate dependencies with syntactic information.

The parsed LXX (used to populate some principal parts) comes from [katabiblon.com](https://en.katabiblon.com/us/index.php?text=LXX).

The lexicon comes from [Dodson's Greek lexicon](https://github.com/biblicalhumanities/Dodson-Greek-Lexicon).
