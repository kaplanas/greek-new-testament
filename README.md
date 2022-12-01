# Greek New Testament: syntactic parsing for learners

These scripts do some basic syntactic parsing of the Greek New Testament in order to extract segments (ideally, constituents) that are accessible to early learners, using only the constructions they've been exposed to so far.

I originally wanted to use a feature grammar, but the parsing simply wasn't fast enough at the scale I needed (especially with all the non-local dependencies that were required).  Instead, I'm using a dependency grammar, with labels for relations.

I modified `nltk`'s `DependencyGrammar` class (and some related classes) to allow for some basic feature parsing.  This let me write rules like "an indicative verb can have a subject that is a noun with the same person and number" instead of having to list every lexical item separately.  But it wasn't possible to write rules for all possible dependencies and keep the number of parses under control; I was already getting 100 parses for sentences that were just [6 words long](https://www.youtube.com/watch?v=do5vXn_Rap4).

Instead, I've settled on a hybrid (and somewhat clunky) system that tries to minimize both the number of dependencies I have to record by hand and the number of parses generated for a given sentence.  Some of the techniques I use in service of the latter goal include the following:

- Use feature-based rules for only a few select relationship types:
  - Subjects and verbs (but not for verbs that allow nominative arguments)
  - Non-nominative verb arguments
  - Second-position clitics
  - Adjectives modifying nouns
  - Determiners of nouns and of adjectives used as substantives
- Use individually recorded dependencies for everything else, especially for prepositions, where the small number of items makes spurious dependencies highly likely in a given sentence
- Annotate rules with position constraints: the dependent must come before or after its head (adjacent or not), or in any position; for each rule, use the narrowest constraint allowed by the corpus
- Tag individual instances of καί and ἤ with the parts of speech they conjoin; since they can combine practically anything, this helps cut down on the number of spurious dependencies elsewhere

The parsing is _not_ intended to be theoretically sophisticated.  My goal is to have a decent representation of the constituent structure for each sentence, for the purpose of automatically extracting meaningful phrases.  The labels are somewhat idiosyncratic, and are drastically oversimplified.

The morphological parsing of [James Tauber](https://github.com/morphgnt/sblgnt) is used as a base.

The parsed LXX (used to populate some principal parts) comes from [katabiblon.com](https://en.katabiblon.com/us/index.php?text=LXX).
