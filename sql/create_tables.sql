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
  NounClass varchar(50),
  VerbClass varchar(20),
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
  FeatureValue varchar(50),
  Required boolean NOT NULL DEFAULT false,
  PRIMARY KEY(StudentID, Feature, FeatureValue)
);

INSERT INTO students_words
(StudentID, Feature, FeatureValue)
VALUES
(1, 'POS', 'personal pronoun'),
(1, 'NounClass', 'second declension'),
(1, 'NounClass', 'Ihsous'),
(1, 'TenseMood', 'present-indicative'),
(1, 'Voice', 'active'),
(1, 'VerbClass', 'omega'),
(1, 'VerbClass', 'eimi');

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
(1, 'subject, non-nominative'),
(1, 'predicate, nominative'),
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
(1, 'predicate, genitive'),
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
(1, 'predicate, dative'),
(1, 'dative, other'),
(1, 'direct object'),
(1, 'accusative, time'),
(1, 'accusative, amount'),
(1, 'accusative, manner'),
(1, 'accusative, cognate of verb'),
(1, 'accusative, other')
;
