CREATE TABLE words (
  Book varchar(10) NOT NULL,
  Chapter integer NOT NULL,
  Verse integer NOT NULL,
  VersePosition integer NOT NULL,
  SentenceID varchar(50) NOT NULL,
  SentencePosition integer NOT NULL,
  Lemma varchar(50) NOT NULL,
  Wordform varchar(50) NOT NULL,
  POS varchar(50) NOT NULL,
  Gender varchar(10),
  Number varchar(10),
  NCase varchar(20),
  Person varchar(10),
  Tense varchar(20),
  Voice varchar(20),
  Mood varchar(20),
  Degree varchar(20),
  NominalType varchar(100),
  NounClassType varchar(100),
  CaseType varchar(100),
  VerbClassType varchar(100),
  PRIMARY KEY(Book, Chapter, Verse, VersePosition),
  INDEX words_sentence_id_position (SentenceID, SentencePosition)
);

CREATE TABLE strings (
  SentenceID varchar(50) NOT NULL,
  Citation varchar(50) NOT NULL,
  Start integer NOT NULL,
  Stop integer NOT NULL,
  String varchar(1000) NOT NULL,
  PRIMARY KEY(SentenceID, Start, Stop)
);

CREATE TABLE relations (
  SentenceID varchar(50) NOT NULL,
  HeadPos integer NOT NULL,
  DependentPos integer NOT NULL,
  FirstPos integer NOT NULL,
  LastPos integer NOT NULL,
  Relation varchar(100) NOT NULL,
  PRIMARY KEY(SentenceID, HeadPos, DependentPos)
);

CREATE TABLE checked_relation_types (
  CheckOrder integer NOT NULL AUTO_INCREMENT,
  Relation varchar(100) NOT NULL,
  PRIMARY KEY(CheckOrder)
);

CREATE TABLE checked_relation_tokens (
  SentenceID varchar(50) NOT NULL,
  HeadPos integer NOT NULL,
  DependentPos integer NOT NULL,
  Relation varchar(100) NOT NULL,
  PRIMARY KEY(SentenceID, HeadPos, DependentPos)
);

CREATE TABLE checked_types (
  SentenceID varchar(50) NOT NULL,
  SentencePosition integer NOT NULL,
  NominalType varchar(100),
  NounClassType varchar(100),
  CaseType varchar(100),
  VerbClassType varchar(100)
);

CREATE TABLE students (
  StudentID integer NOT NULL AUTO_INCREMENT,
  StudentUsername varchar(100) NOT NULL,
  StudentName varchar(100) NOT NULL,
  PRIMARY KEY(StudentID)
);

INSERT INTO students
  (StudentName, StudentUsername)
  VALUES
  ('test_student', 'Test Student');

CREATE TABLE students_words (
  StudentID integer,
  Feature varchar(50),
  FeatureValue varchar(100),
  Required boolean NOT NULL DEFAULT false,
  PRIMARY KEY(StudentID, Feature, FeatureValue)
);

INSERT INTO students_words
(StudentID, Feature, FeatureValue)
VALUES
(1, 'POS', 'verb'),
(1, 'POS', 'personal pronoun'),
(1, 'NominalType', 'pronoun'),
(1, 'POS', 'noun'),
(1, 'NominalType', 'noun'),
(1, 'NounClassType', 'second declension'),
(1, 'NounClassType', 'Ihsous'),
(1, 'TenseMood', 'present-indicative'),
(1, 'Voice', 'active'),
(1, 'VerbClassType', 'omega'),
(1, 'VerbClassType', 'eimi'),
(1, 'NounClassType', 'first declension'),
(1, 'POS', 'conj'),
(1, 'POS', 'personal pronoun with kai'),
(1, 'POS', 'negation'),
(1, 'VerbClass', 'contract, ew'),
(1, 'VerbClass', 'contract, aw'),
(1, 'VerbClass', 'contract, ow'),
(1, 'NounClassType', 'second declension with hs'),
(1, 'POS', 'det'),
(1, 'POS', 'adj'),
(1, 'NominalType', 'adjective'),
(1, 'NounClassType', 'first/second declension'),
(1, 'TenseMood', 'imperfect-indicative'),
(1, 'POS', 'ptcl'),
(1, 'POS', 'prep'),
(1, 'POS', 'demonstrative pronoun'),
(1, 'POS', 'demonstrative pronoun with kai'),
(1, 'POS', 'reflexive pronoun'),
(1, 'TenseMood', 'future-indicative'),
(1, 'TenseMood', 'present-infinitive'),
(1, 'TenseMood', 'future-infinitive'),
(1, 'POS', 'adv'),
(1, 'POS', 'adverb with kai'),
(1, 'POS', 'indefinite adverb'),
(1, 'Voice', 'middle'),
(1, 'POS', 'relative pronoun'),
(1, 'NominalType', 'relative clause'),
(1, 'NounClassType', 'third declension, consonant stem'),
(1, 'NounClassType', 'third declension, vowel stem'),
(1, 'NounClassType', 'first/second declension; third declension, consonant stem'),
(1, 'NounClassType', 'irregular'),
(1, 'NounClassType', 'undeclined'),
(1, 'POS', 'indefinite pronoun'),
(1, 'POS', 'interrogative pronoun'),
(1, 'TenseMood', 'aorist-indicative'),
(1, 'TenseMood', 'aorist-infinitive'),
(1, 'VerbClassType', 'mi'),
(1, 'POS', 'number')
;

CREATE TABLE students_relations (
  StudentID integer,
  Relation varchar(100) NOT NULL,
  Required boolean NOT NULL DEFAULT false,
  PRIMARY KEY(StudentID, Relation)
);

INSERT INTO students_relations
(StudentID, Relation)
VALUES
(1, 'subject'),
(1, 'subject, neuter plural'),
(1, 'subject, neuter plural, regular agreement'),
(1, 'subject, irregular agreement'),
(1, 'subject of verbless predicate'),
(1, 'predicate, nominal'),
(1, 'genitive, relation'),
(1, 'genitive, body part'),
(1, 'genitive, subject'),
(1, 'genitive, possession'),
(1, 'genitive, object'),
(1, 'genitive, part-whole'),
(1, 'genitive, source'),
(1, 'genitive, characterized by'),
(1, 'genitive, location'),
(1, 'genitive, specification'),
(1, 'genitive, material'),
(1, 'genitive, time'),
(1, 'genitive, comparison'),
(1, 'genitive, property'),
(1, 'genitive, about'),
(1, 'genitive, contents'),
(1, 'genitive, son of'),
(1, 'genitive, amount'),
(1, 'genitive, direct object'),
(1, 'genitive, other'),
(1, 'indirect object'),
(1, 'dative, instrument'),
(1, 'dative, benefit'),
(1, 'dative, time'),
(1, 'dative, manner'),
(1, 'dative, possession'),
(1, 'dative, agent'),
(1, 'dative, cognate of verb'),
(1, 'dative, Hebrew infinitive construct'),
(1, 'direct object, dative'),
(1, 'dative, other'),
(1, 'direct object'),
(1, 'accusative, time'),
(1, 'accusative, amount'),
(1, 'accusative, manner'),
(1, 'accusative, cognate of verb'),
(1, 'accusative, other'),
(1, 'interjection, vocative'),
(1, 'conjunct'),
(1, 'conjunct, chain'),
(1, 'conjunct, μέν δέ'),
(1, 'second-position clitic'),
(1, 'negation of verb'),
(1, 'negation of verb, semantically embedded'),
(1, 'negation of nominal'),
(1, 'negation, double'),
(1, 'negation, other'),
(1, 'determiner'),
(1, 'determiner, things of'),
(1, 'modifier of nominal, nominal'),
(1, 'modifier of non-nominal, adjective'),
(1, 'argument of adjective'),
(1, 'argument of adjective, nominal'),
(1, 'subject of small clause'),
(1, 'conjunct, main'),
(1, 'conjunct, subordinate'),
(1, 'conjunct, ὅτι'),
(1, 'sentential complement'),
(1, 'particle'),
(1, 'predicate, non-nominal'),
(1, 'object of preposition'),
(1, 'modifier of verb, PP'),
(1, 'modifier of verbless predicate, PP'),
(1, 'modifier of nominal, PP'),
(1, 'modifier of adjective, PP'),
(1, 'modifier of other, PP'),
(1, 'infinitive argument of verb'),
(1, 'infinitive argument of noun'),
(1, 'infinitive, purpose'),
(1, 'infinitive, something'),
(1, 'modifier of verb, infinitive'),
(1, 'modifier of nominal, infinitive'),
(1, 'subject of infinitive'),
(1, 'modifier of verb, adverb'),
(1, 'modifier of verbless predicate, adverb'),
(1, 'modifier of nominal, adverb'),
(1, 'modifier of adjective, adverb'),
(1, 'modifier of other, adverb'),
(1, 'resumptive pronoun'),
(1, 'direct object, attraction'),
(1, 'indirect object, attraction'),
(1, 'subject, attraction'),
(1, 'subject of infinitive, attraction'),
(1, 'other, attraction'),
(1, 'modifier of verb, nominal'),
(1, 'modifier of verbless predicate, nominal'),
(1, 'title'),
(1, 'entitled'),
(1, 'name'),
(1, 'number')
;
