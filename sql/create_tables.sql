CREATE TABLE books (
  Book varchar(10) NOT NULL,
  BookName varchar(50) NOT NULL,
  BookOrder integer NOT NULL,
  PRIMARY KEY(Book)
);

INSERT INTO books
  (Book, BookName, BookOrder)
  VALUES
  ('Matt', 'Matthew', 1),
  ('Mark', 'Mark', 2),
  ('Luke', 'Luke', 3),
  ('John', 'John', 4),
  ('Acts', 'Acts', 5),
  ('Rom', 'Romans', 6),
  ('1Cor', '1 Corinthians', 7),
  ('2Cor', '2 Corinthians', 8),
  ('Gal', 'Galatians', 9),
  ('Eph', 'Ephesians', 10),
  ('Phil', 'Philippians', 11),
  ('Col', 'Colossians', 12),
  ('1Thess', '1 Thessalonians', 13),
  ('2Thess', '2 Thessalonians', 14),
  ('1Tim', '1 Timothy', 15),
  ('2Tim', '2 Timothy', 16),
  ('Titus', 'Titus', 17),
  ('Phlm', 'Philemon', 18),
  ('Heb', 'Hebrews', 19),
  ('Jas', 'James', 20),
  ('1Pet', '1 Peter', 21),
  ('2Pet', '2 Peter', 22),
  ('1John', '1 John', 23),
  ('2John', '2 John', 24),
  ('3John', '3 John', 25),
  ('Jude', 'Jude', 26),
  ('Rev', 'Revelation', 27);

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

CREATE TABLE lessons (
  LessonName varchar(100) NOT NULL,
  DisplayOrder integer NOT NULL,
  LessonGroup varchar(100) NOT NULL,
  PRIMARY KEY(LessonName)
);

INSERT INTO lessons
  (LessonName, DisplayOrder, LessonGroup)
  VALUES
  ('Second declension', 1, 'Noun class'),
  ('First declension', 2, 'Noun class'),
  ('Third declension', 3, 'Noun class'),
  ('Ἰησοῦς', 4, 'Noun class'),
  ('Irregular', 5, 'Noun class'),
  ('Undeclined', 6, 'Noun class'),
  ('Εἰμί', 1, 'Verb class'),
  ('Omega', 2, 'Verb class'),
  ('Contract, έω', 3, 'Verb class'),
  ('Contract, άω', 4, 'Verb class'),
  ('Contract, όω', 5, 'Verb class'),
  ('Μί', 6, 'Verb class'),
  ('Οἴδα', 7, 'Verb class'),
  ('Other', 8, 'Verb class'),
  ('Present indicative', 1, 'Tense and mood'),
  ('Future indicative', 2, 'Tense and mood'),
  ('Imperfect indicative', 3, 'Tense and mood'),
  ('Aorist indicative', 4, 'Tense and mood'),
  ('Present infinitive', 5, 'Tense and mood'),
  ('Future infinitive', 6, 'Tense and mood'),
  ('Aorist infinitive', 7, 'Tense and mood'),
  ('Active', 1, 'Voice'),
  ('Middle', 2, 'Voice'),
  ('Passive', 3, 'Voice'),
  ('Personal pronouns', 1, 'Other parts of speech'),
  ('Reflexive pronouns', 2, 'Other parts of speech'),
  ('Demonstrative pronouns', 3, 'Other parts of speech'),
  ('Interrogative pronouns', 4, 'Other parts of speech'),
  ('Indefinite pronouns', 5, 'Other parts of speech'),
  ('Relative pronouns', 6, 'Other parts of speech'),
  ('Conjunctions', 7, 'Other parts of speech'),
  ('Subjects', 1, 'Arguments of verbs'),
  ('Direct objects', 2, 'Arguments of verbs'),
  ('Indirect objects', 3, 'Arguments of verbs'),
  ('Coordinating conjunctions', 1, 'Conjunction'),
  ('Subordinating conjunctions', 2, 'Conjunction'),
  ('Μὲν δέ', 3, 'Conjunction'),
  ('Ὡς', 4, 'Conjunction');

CREATE TABLE students_lessons (
  StudentID integer NOT NULL,
  LessonName varchar(100) NOT NULL,
  PRIMARY KEY(StudentID, LessonName),
  FOREIGN KEY (StudentID) REFERENCES students(StudentID) ON DELETE RESTRICT,
  FOREIGN KEY (LessonName) REFERENCES lessons(LessonName) ON DELETE RESTRICT
);

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
(1, 'POS', 'number'),
(1, 'TenseMood', 'present-participle'),
(1, 'TenseMood', 'future-participle'),
(1, 'TenseMood', 'aorist-participle'),
(1, 'NominalType', 'participle'),
(1, 'Degree', 'comparative'),
(1, 'Degree', 'superlative'),
(1, 'TenseMood', 'present-subjunctive'),
(1, 'TenseMood', 'aorist-subjunctive'),
(1, 'TenseMood', 'present-optative'),
(1, 'TenseMood', 'aorist-optative')
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
(1, 'genitive, comparative'),
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
(1, 'number'),
(1, 'modifier of verb, participle'),
(1, 'modifier of other, participle'),
(1, 'subject of participle'),
(1, 'comparative'),
(1, 'conjunct, ἤ')
;
