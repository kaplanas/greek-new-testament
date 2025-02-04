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
  LemmaSort varchar(50) NOT NULL,
  POS varchar(50) NOT NULL,
  PrincipalParts varchar(1000),
  ShortDefinition varchar(4000),
  PRIMARY KEY(Lemma, POS)
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
  ColumnName varchar(10) NOT NULL UNIQUE,
  PRIMARY KEY(LessonID)
);

INSERT INTO lessons
  (LessonName, DisplayOrder, LessonGroup, ColumnName)
  VALUES
  ('Nominative', 1, 'Case', 'nom'),
  ('Genitive', 2, 'Case', 'gen'),
  ('Dative', 3, 'Case', 'dat'),
  ('Accusative', 4, 'Case', 'acc'),
  ('Vocative', 5, 'Case', 'voc'),
  ('Second declension', 1, 'Noun class', 'n_2'),
  ('First declension', 2, 'Noun class', 'n_1'),
  ('Third declension', 3, 'Noun class', 'n_3'),
  ('Ἰησοῦς', 4, 'Noun class', 'n_Ihsous'),
  ('Irregular', 5, 'Noun class', 'n_irr'),
  ('Undeclined', 6, 'Noun class', 'n_undec'),
  ('First and second declension', 1, 'Adjective class', 'a_12'),
  ('Second declension', 2, 'Adjective class', 'a_2'),
  ('Third declension', 3, 'Adjective class', 'a_3'),
  ('Irregular', 4, 'Adjective class', 'a_irr'),
  ('Comparatives', 1, 'Adjective forms', 'comp'),
  ('Superlatives', 2, 'Adjective forms', 'super'),
  ('Εἰμί', 1, 'Verb class', 'eimi'),
  ('Omega', 2, 'Verb class', 'omega'),
  ('Contract, έω', 3, 'Verb class', 'c_ew'),
  ('Contract, άω', 4, 'Verb class', 'c_aw'),
  ('Contract, όω', 5, 'Verb class', 'c_ow'),
  ('Μί', 6, 'Verb class', 'mi'),
  ('Οἶδα', 7, 'Verb class', 'oida'),
  ('Other', 8, 'Verb class', 'v_other'),
  ('Present indicative', 1, 'Tense and mood', 'pres_ind'),
  ('Future indicative', 2, 'Tense and mood', 'fut_ind'),
  ('Imperfect indicative', 3, 'Tense and mood', 'imp_ind'),
  ('Aorist indicative', 4, 'Tense and mood', 'aor_ind'),
  ('Perfect indicative', 5, 'Tense and mood', 'per_ind'),
  ('Pluperfect indicative', 6, 'Tense and mood', 'plu_ind'),
  ('Present infinitive', 7, 'Tense and mood', 'pres_inf'),
  ('Future infinitive', 8, 'Tense and mood', 'fut_inf'),
  ('Aorist infinitive', 9, 'Tense and mood', 'aor_inf'),
  ('Perfect infinitive', 10, 'Tense and mood', 'per_inf'),
  ('Present participle', 11, 'Tense and mood', 'pres_part'),
  ('Future participle', 12, 'Tense and mood', 'fut_part'),
  ('Aorist participle', 13, 'Tense and mood', 'aor_part'),
  ('Perfect participle', 14, 'Tense and mood', 'per_part'),
  ('Present imperative', 15, 'Tense and mood', 'pres_imp'),
  ('Aorist imperative', 16, 'Tense and mood', 'aor_imp'),
  ('Perfect imperative', 17, 'Tense and mood', 'per_imp'),
  ('Present subjunctive', 18, 'Tense and mood', 'pres_sub'),
  ('Aorist subjunctive', 19, 'Tense and mood', 'aor_sub'),
  ('Perfect subjunctive', 20, 'Tense and mood', 'per_sub'),
  ('Present optative', 21, 'Tense and mood', 'pres_opt'),
  ('Aorist optative', 22, 'Tense and mood', 'aor_opt'),
  ('Active', 1, 'Voice', 'act'),
  ('Middle', 2, 'Voice', 'mid'),
  ('Passive', 3, 'Voice', 'pas'),
  ('Personal pronouns', 1, 'Pronouns', 'p_pers'),
  ('Reflexive pronouns', 2, 'Pronouns', 'p_refl'),
  ('Demonstrative pronouns', 3, 'Pronouns', 'p_demo'),
  ('Interrogative pronouns', 4, 'Pronouns', 'p_inter'),
  ('Indefinite pronouns', 5, 'Pronouns', 'p_indef'),
  ('Relative pronouns', 6, 'Pronouns', 'p_rel'),
  ('Definite article', 1, 'Other parts of speech', 'def'),
  ('Second-position clitics', 2, 'Other parts of speech', 'clitic'),
  ('Prepositions', 3, 'Other parts of speech', 'prep'),
  ('Coordinating conjunctions', 4, 'Other parts of speech', 'coord'),
  ('Subordinating conjunctions', 5, 'Other parts of speech', 'subord'),
  ('Negation', 6, 'Other parts of speech', 'neg'),
  ('Adverbs', 7, 'Other parts of speech', 'adv'),
  ('Numbers', 8, 'Other parts of speech', 'num'),
  ('Particles', 9, 'Other parts of speech', 'part'),
  ('Comparison', 1, 'Syntactic structures', 'comps'),
  ('Indirect discourse', 2, 'Syntactic structures', 'disc'),
  ('Topics', 3, 'Syntactic structures', 'top');

CREATE TABLE students_lessons (
  StudentID integer NOT NULL,
  LessonID integer NOT NULL,
  PRIMARY KEY(StudentID, LessonID),
  FOREIGN KEY (StudentID) REFERENCES students(StudentID) ON DELETE RESTRICT,
  FOREIGN KEY (LessonID) REFERENCES lessons(LessonID) ON DELETE RESTRICT
);
