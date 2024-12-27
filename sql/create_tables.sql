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

CREATE TABLE relations (
  SentenceID varchar(50) NOT NULL,
  HeadPos integer NOT NULL,
  DependentPos integer NOT NULL,
  FirstPos integer NOT NULL,
  LastPos integer NOT NULL,
  Relation varchar(100) NOT NULL,
  PRIMARY KEY(SentenceID, HeadPos, DependentPos)
);

CREATE TABLE lemmas (
  Lemma varchar(50) NOT NULL,
  ShortDefinition varchar(1000),
  PRIMARY KEY(Lemma)
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

CREATE TABLE strings (
  SentenceID varchar(50) NOT NULL,
  Citation varchar(50) NOT NULL,
  Start integer NOT NULL,
  Stop integer NOT NULL,
  String varchar(1000) NOT NULL,
  PRIMARY KEY(SentenceID, Start, Stop)
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
  LessonID integer NOT NULL AUTO_INCREMENT,
  LessonName varchar(100) NOT NULL,
  DisplayOrder integer NOT NULL,
  LessonGroup varchar(100) NOT NULL,
  PRIMARY KEY(LessonID)
);

INSERT INTO lessons
  (LessonName, DisplayOrder, LessonGroup)
  VALUES
  ('Nominative', 1, 'Case'),
  ('Genitive', 2, 'Case'),
  ('Dative', 3, 'Case'),
  ('Accusative', 4, 'Case'),
  ('Vocative', 5, 'Case'),
  ('Second declension', 1, 'Noun class'),
  ('First declension', 2, 'Noun class'),
  ('Third declension', 3, 'Noun class'),
  ('Ἰησοῦς', 4, 'Noun class'),
  ('Irregular', 5, 'Noun class'),
  ('Undeclined', 6, 'Noun class'),
  ('First and second declension', 1, 'Adjective class'),
  ('Second declension', 2, 'Adjective class'),
  ('Third declension', 3, 'Adjective class'),
  ('Irregular', 4, 'Adjective class'),
  ('Undeclined', 5, 'Adjective class'),
  ('Comparatives', 1, 'Adjective forms'),
  ('Superlatives', 2, 'Adjective forms'),
  ('Εἰμί', 1, 'Verb class'),
  ('Omega', 2, 'Verb class'),
  ('Contract, έω', 3, 'Verb class'),
  ('Contract, άω', 4, 'Verb class'),
  ('Contract, όω', 5, 'Verb class'),
  ('Μί', 6, 'Verb class'),
  ('Οἶδα', 7, 'Verb class'),
  ('Other', 8, 'Verb class'),
  ('Present indicative', 1, 'Tense and mood'),
  ('Future indicative', 2, 'Tense and mood'),
  ('Imperfect indicative', 3, 'Tense and mood'),
  ('Aorist indicative', 4, 'Tense and mood'),
  ('Perfect indicative', 5, 'Tense and mood'),
  ('Pluperfect indicative', 6, 'Tense and mood'),
  ('Present infinitive', 7, 'Tense and mood'),
  ('Future infinitive', 8, 'Tense and mood'),
  ('Aorist infinitive', 9, 'Tense and mood'),
  ('Perfect infinitive', 10, 'Tense and mood'),
  ('Present participle', 11, 'Tense and mood'),
  ('Future participle', 12, 'Tense and mood'),
  ('Aorist participle', 13, 'Tense and mood'),
  ('Perfect participle', 14, 'Tense and mood'),
  ('Present imperative', 15, 'Tense and mood'),
  ('Aorist imperative', 16, 'Tense and mood'),
  ('Perfect imperative', 17, 'Tense and mood'),
  ('Present subjunctive', 18, 'Tense and mood'),
  ('Aorist subjunctive', 19, 'Tense and mood'),
  ('Perfect subjunctive', 20, 'Tense and mood'),
  ('Present optative', 21, 'Tense and mood'),
  ('Aorist optative', 22, 'Tense and moood'),
  ('Active', 1, 'Voice'),
  ('Middle', 2, 'Voice'),
  ('Passive', 3, 'Voice'),
  ('Personal pronouns', 1, 'Pronouns'),
  ('Reflexive pronouns', 2, 'Pronouns'),
  ('Demonstrative pronouns', 3, 'Pronouns'),
  ('Interrogative pronouns', 4, 'Pronouns'),
  ('Indefinite pronouns', 5, 'Pronouns'),
  ('Relative pronouns', 6, 'Pronouns'),
  ('Definite article', 1, 'Other parts of speech'),
  ('Second-position clitics', 2, 'Other parts of speech'),
  ('Prepositions', 3, 'Other parts of speech'),
  ('Coordinating conjunctions', 4, 'Other parts of speech'),
  ('Subordinating conjunctions', 5, 'Other parts of speech'),
  ('Negation', 6, 'Other parts of speech'),
  ('Adverbs', 7, 'Other parts of speech'),
  ('Numbers', 8, 'Other parts of speech'),
  ('Particles', 9, 'Other parts of speech'),
  ('Comparison', 1, 'Syntactic structures'),
  ('Indirect discourse', 2, 'Syntactic structures'),
  ('Topics', 3, 'Syntactic structures');

CREATE TABLE students_lessons (
  StudentID integer NOT NULL,
  LessonID integer NOT NULL,
  PRIMARY KEY(StudentID, LessonID),
  FOREIGN KEY (StudentID) REFERENCES students(StudentID) ON DELETE RESTRICT,
  FOREIGN KEY (LessonID) REFERENCES lessons(LessonID) ON DELETE RESTRICT
);
