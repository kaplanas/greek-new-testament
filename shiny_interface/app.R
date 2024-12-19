library(shiny)
library(RMySQL)
library(tidyverse)
library(glue)
library(bslib)
library(DT)

source("database_connection_local.R", local = T)

#### Get starting data ####

# Database connection
gnt.con = dbConnect(MySQL(), user = db.user, password = db.password,
                    dbname = "gnt", host = db.host, port = 3306)

# Set character encoding
dbGetQuery(gnt.con, "SET NAMES utf8")

# List of lessons
lessons.df = dbGetQuery(gnt.con,
                        "SELECT LessonID, LessonName, LessonGroup
                         FROM lessons
                         ORDER BY DisplayOrder")

# Lessons required for cases
case.required = list(
  "nominative" = "Nominative",
  "genitive" = "Genitive",
  "dative" = "Dative",
  "accusative" = "Accusative",
  "vocative" = "Vocative"
)

# Lessons required for noun classes
noun.class.required = list(
  "second declension" = c("Second declension"),
  "first declension" = c("First declension"),
  "first declension with hs" = c("Second declension", "First declension"),
  "third declension, consonant stem" = c("Third declension"),
  "third declension, vowel stem" = c("Third declension"),
  "Ihsous" = c("Ἰησοῦς"),
  "irregular" = c("Irregular"),
  "undeclined" = c("Undeclined")
)

# Lessons required for comparative and superlative adjectives
adjective.degree.required = list(
  "comparative" = "Comparatives",
  "superlative" = "Superlatives"
)

# Lessons required for adjective classes
adjective.class.required = list(
  "first/second declension" = c("First and second declension"),
  "third declension, consonant stem" = c("Third declension"),
  "third declension, vowel stem" = c("Third declension"),
  "first/second declension; third declension, consonant stem" = c("First and second declension", "Third declension"),
  "irregular" = c("Irregular"),
  "undeclined" = c("Undeclined")
)

# Lessons required for verb classes
verb.class.required = list(
  "eimi" = "Εἰμί",
  "omega" = "Omega",
  "contract, ew" = "Contract, έω",
  "contract, aw" = "Contract, άω",
  "contract, ow" = "Contract, όω",
  "mi" = "Μί",
  "oida" = "Οἴδα",
  "other" = "Other"
)

# Lessons required for voice
voice.required = list(
  "active" = "Active",
  "middle" = "Middle",
  "passive" = "Passive"
)

# Lessons required for tense and mood
tense.mood.required = list(
  "present-indicative" = "Present indicative",
  "future-indicative" = "Future indicative",
  "imperfect-indicative" = "Imperfect indicative",
  "aorist-indicative" = "Aorist indicative",
  "perfect-indicative" = "Perfect indicative",
  "pluperfect-indicative" = "Pluperfect indicative",
  "present-infinitive" = "Present infinitive",
  "future-infinitive" = "Future infinitive",
  "aorist-infinitive" = "Aorist infinitive",
  "perfect-infinitive" = "Perfect infinitive",
  "present-participle" = "Present participle",
  "future-participle" = "Future participle",
  "aorist-participle" = "Aorist participle",
  "perfect-participle" = "Perfect participle",
  "present-imperative" = "Present imperative",
  "aorist-imperative" = "Aorist imperative",
  "perfect-imperative" = "Perfect imperative",
  "present-subjunctive" = "Present subjunctive",
  "aorist-subjunctive" = "Aorist subjunctive",
  "perfect-subjunctive" = "Perfect subjunctive",
  "present-optative" = "Present optative",
  "aorist-optative" = "Aorist optative"
)

# Lessons required for various parts of speech
other.pos.required = list(
  "personal pronoun" = c("Personal pronouns"),
  "personal pronoun with kai" = c("Personal pronouns", "Coordinating conjunctions"),
  "reflexive pronoun" = c("Reflexive pronouns"),
  "demonstrative pronoun" = c("Demonstrative pronouns"),
  "demonstrative pronoun with kai" = c("Demonstrative pronouns", "Coordinating conjunctions"),
  "interrogative pronoun" = c("Interrogative pronouns"),
  "indefinite pronoun" = c("Indefinite pronouns"),
  "relative pronoun" = c("Relative pronouns"),
  "det" = c("Definite article"),
  "prep" = c("Prepositions"),
  "negation" = c("Negation"),
  "adv" = c("Adverbs"),
  "adverb with kai" = c("Adverbs", "Coordinating conjunctions"),
  "indefinite adverb" = c("Adverbs", "Indefinite pronouns"),
  "interrogative adverb" = c("Adverbs", "Interrogative pronouns"),
  "reflexive adverb" = c("Adverbs", "Reflexive pronouns"),
  "num" = c("Numbers"),
  "ptcl" = c("Particles"),
  "intj" = c("Particles")
)

# Lessons required for various relations
relation.required = list(
  "sentential complement" = c("Sentential complements"),
  "conjunct, ὅτι" = c("Sentential complements"),
  "clause argument of verb" = c("Sentential complements"),
  "second-position clitic" = c("Second-position clitics"),
  "conjunct" = c("Coordinating conjunctions"),
  "conjunct, main" = c("Subordinating conjunctions"),
  "conjunct, subordinate" = c("Subordinating conjunctions"),
  "conjunct, ὡς, clause" = c("Subordinating conjunctions"),
  "conjunct, ὡς, non-clause" = c("Subordinating conjunctions"),
  "conjunct, ὡς, other" = c("Subordinating conjunctions"),
  "topic" = c("Topics"),
  "subject, attraction" = c("Relative pronouns"),
  "direct object, attraction" = c("Relative pronouns"),
  "indirect object, attraction" = c("Relative pronouns"),
  "other, attraction" = c("Relative pronouns"),
  "resumptive pronoun" = c("Relative pronouns"),
  "number" = c("Numbers")
)

# Pretty names for word properties
word.property.names.df = bind_rows(
  data.frame(property = "NounClassType",
             pretty.property = "Noun class",
             value = c("second declension", "first declension",
                       "first declension with hs",
                       "third declension, consonant stem",
                       "third declension, vowel stem", "Ihsous", "irregular",
                       "undeclined")) %>%
    mutate(pretty.value = case_when(value == "first declension with hs" ~ "First declension with ης",
                                    grepl("^third declension", value) ~ "Third declension",
                                    value == "Ihsous" ~ "Ἰησοῦς",
                                    T ~ str_to_sentence(value))),
  data.frame(property = "VerbClassType",
             pretty.property = "Verb class",
             value = c("eimi", "omega", "contract, ew", "contract, aw",
                       "contract, ow", "mi", "oida", "other"),
             pretty.value = c("Εἰμί", "Omega", "Contract, έω", "Contract, άω",
                              "Contract, όω", "Μί", "Οἴδα", "Other")),
  data.frame(property = "TenseMood",
             pretty.property = "Tense and mood",
             value = c("present-indicative", "future-indicative",
                       "imperfect-indicative", "aorist-indicative",
                       "perfect-indicative", "pluperfect-indicative",
                       "present-infinitive", "future-infinitive",
                       "aorist-infinitive", "perfect-infinitive",
                       "present-participle", "future-participle",
                       "aorist-participle", "perfect-participle",
                       "present-imperative", "aorist-imperative",
                       "perfect-imperative", "present-subjunctive",
                       "aorist-subjunctive", "perfect-subjunctive",
                       "present-optative", "aorist-optative")) %>%
    mutate(pretty.value = str_to_sentence(gsub("-", " ", value))),
  data.frame(property = "Voice",
             pretty.property = "Voice",
             value = c("active", "middle", "passive")) %>%
    mutate(pretty.value = str_to_sentence(value))
)

# Pretty names for relations
relation.names.df = data.frame(
  relation = c("accusative, amount", "accusative, cognate of verb",
               "accusative, manner", "accusative, other", "accusative, time",
               "argument of adjective", "argument of adjective, infinitive",
               "argument of adjective, nominal", "clause argument of verb",
               "comparative", "conjunct", "conjunct, main",
               "conjunct, subordinate", "conjunct, ἤ", "conjunct, μέν δέ",
               "conjunct, ὅτι", "conjunct, ὡς, clause",
               "conjunct, ὡς, non-clause", "conjunct, ὡς, other",
               "dative, agent", "dative, benefit", "dative, cognate of verb",
               "dative, Hebrew infinitive construct", "dative, instrument",
               "dative, manner", "dative, other", "dative, possession",
               "dative, time", "determiner, things of", "direct object",
               "direct object, attraction", "genitive, about",
               "genitive, amount", "genitive, body part",
               "genitive, characterized by", "genitive, comparative",
               "genitive, contents", "genitive, location", "genitive, material",
               "genitive, object", "genitive, other", "genitive, part-whole",
               "genitive, possession", "genitive, property",
               "genitive, relation", "genitive, son of", "genitive, source",
               "genitive, specification", "genitive, subject", "genitive, time",
               "indirect object", "indirect object, attraction",
               "infinitive argument of noun", "infinitive argument of verb",
               "infinitive, purpose", "infinitive, something",
               "modifier of adjective, adverb", "modifier of adjective, PP",
               "modifier of nominal, adverb", "modifier of nominal, infinitive",
               "modifier of nominal, nominal", "modifier of nominal, PP",
               "modifier of non-nominal, adjective",
               "modifier of other, adverb", "modifier of other, nominal",
               "modifier of other, participle", "modifier of other, PP",
               "modifier of verb, adverb", "modifier of verb, infinitive",
               "modifier of verb, nominal", "modifier of verb, participle",
               "modifier of verb, PP", "modifier of verbless predicate, adverb",
               "modifier of verbless predicate, nominal",
               "modifier of verbless predicate, participle",
               "modifier of verbless predicate, PP", "negation of nominal",
               "negation of verb", "negation of verb, semantically embedded",
               "negation, other", "negation, εἰ μὴ", "negation, εἰ μὴ, nominal",
               "number", "object of preposition", "other, attraction",
               "predicate, nominal", "predicate, non-nominal",
               "resumptive pronoun", "sentential complement", "subject",
               "subject of implicit speech", "subject of infinitive",
               "subject of infinitive, attraction", "subject of participle",
               "subject of verbless predicate", "subject, attraction",
               "subject, irregular agreement", "topic")
) %>%
  mutate(pretty.relation = case_when(grepl("^argument of adjective", relation) ~ "Argument of adjective",
                                     relation %in% c("comparative",
                                                     "conjunct, ἤ") ~ "Comparison",
                                     relation == "conjunct" ~ "Conjunction, coordinating",
                                     relation %in% c("conjunct, main",
                                                     "conjunct, subordinate") ~ "Conjunction, subordinating",
                                     relation == "conjunct, μέν δέ" ~ "Μὲν...δέ...",
                                     relation %in% c("conjunct, ὅτι",
                                                     "sentential complement") ~ "Indirect discourse",
                                     relation %in% c("conjunct, ὡς, clause",
                                                     "conjunct, ὡς, non-clause",
                                                     "conjunct, ὡς, other") ~ "Ὡς",
                                     relation == "determiner, things of" ~ "\"Things of\"",
                                     relation == "negation of verb, semantically embedded" ~ "Negation of verb",
                                     relation %in% c("negation, εἰ μὴ",
                                                     "negation, εἰ μὴ, nominal") ~ "Εἰ μὴ",
                                     relation %in% c("subject, neuter plural",
                                                     "subject, neuter plural, regular agreement") ~ "Subject, neuter plural",
                                     T ~ str_to_sentence(relation)))

#### UI ####

# Page title
page.title = "New Testament Greek"

# Login page
login.page = nav_panel(title = "Log in",
                       textInput("gnt.username", "Username"),
                       passwordInput("gnt.password", "Password"),
                       actionButton("user.log.in", label = "Log in"))

# Page of user's knowledge
knowledge.groups = map(
  set_names(unique(lessons.df$LessonGroup)),
  function(lg) {
    checkboxGroupInput(gsub(" ", ".", lg),
                       lg,
                       lessons.df %>%
                         filter(LessonGroup == lg) %>%
                         pull(LessonName))
  }
)
knowledge.page = nav_panel(title = "Current knowledge",
                           actionButton("update.knowledge", "Save changes"),
                           layout_columns(
                             card(card_header(class = "bg-dark",
                                              "Nouns and adjectives"),
                                  knowledge.groups[["Case"]],
                                  knowledge.groups[["Noun class"]],
                                  knowledge.groups[["Adjective class"]],
                                  knowledge.groups[["Adjective forms"]]),
                             card(card_header(class = "bg-dark", "Verbs"),
                                  knowledge.groups[["Verb class"]],
                                  knowledge.groups[["Voice"]],
                                  knowledge.groups[["Tense and mood"]]),
                             card(card_header(class = "bg-dark", "Other"),
                                  knowledge.groups[["Pronouns"]],
                                  knowledge.groups[["Other parts of speech"]],
                                  knowledge.groups[["Syntactic structures"]])
                           ))
string.page = nav_panel(title = "Excerpts",
                        layout_columns(
                          numericInput("string.count",
                                       "Number of excerpts to show:",
                                       value = 10),
                          selectInput("string.examples", "Include examples of:",
                                      choices = c("[everything]")),
                          fill = F
                        ),
                        actionButton("refresh.strings", "Refresh"),
                        DTOutput("show.strings"))

# Define UI
ui <- page_navbar(
  title = page.title,
  login.page,
  knowledge.page,
  string.page,
  useBusyIndicators()
)

#### Server ####

# Define server logic
server <- function(input, output, session) {
  
  # Student data
  student.id = reactiveVal(NULL)
  knowledge.df = reactiveVal(NULL)
  all.strings.df = reactiveVal(NULL)
  all.word.properties.df = reactiveVal(NULL)
  all.relations.df = reactiveVal(NULL)
  sample.strings.df = reactiveVal(NULL)
  
  # When the user attempts to log in, attempt to create a connection and
  # get the user's data
  observeEvent(input$user.log.in, {
    
    # Is the user authorized?
    authorized.user = F
    
    # Create a connection to make sure this is an authorized user; we won't use
    # this connection for anything else
    tryCatch(
      {
        user.con = dbConnect(MySQL(), user = input$gnt.username,
                             password = input$gnt.password, host = "localhost",
                             port = 3306)
        authorized.user = T
        showNotification("Login successful", type = "message")
      },
      error = function(err) {
        print(err)
        showNotification("Login failed", type = "error")
      },
      finally = {
        if(exists("user.con")) {
          dbDisconnect(user.con)
        }
      }
    )
    
    # If we connected successfully, get some data
    if(authorized.user) {
      
      # Get the user's student ID
      student.id.sql = glue_sql("SELECT StudentID
                                 FROM students
                                 WHERE StudentUsername = {input$gnt.username}",
                                .con = gnt.con)
      student.id(dbGetQuery(gnt.con, student.id.sql)$StudentID)

      # Get the student's current knowledge
      knowledge.sql = glue_sql("SELECT LessonID
                                FROM students_lessons
                                WHERE StudentID = {student.id()}",
                               .con = gnt.con)
      knowledge.df(dbGetQuery(gnt.con, knowledge.sql))
      
      # Update knowledge panel with student's current knowledge
      for(cgi in names(knowledge.groups)) {
        updateCheckboxGroupInput(session, inputId = gsub(" ", ".", cgi),
                                 selected = lessons.df %>%
                                   filter(LessonGroup == cgi) %>%
                                   inner_join(knowledge.df(), by = "LessonID") %>%
                                   pull(LessonName))
      }
      
    }
    
  })
  
  # Update the student's knowledge in the database when the user clicks the
  # "save" button
  observeEvent(input$update.knowledge, {
    
    # Update the student's new knowledge
    for(kg in names(knowledge.groups)) {
      delete.sql = "DELETE FROM students_lessons
                    WHERE StudentID = {student.id()}
                          AND LessonID IN (SELECT LessonID
                                             FROM lessons
                                             WHERE LessonGroup = {kg})"
      new.ids = lessons.df %>%
        filter(LessonGroup == kg,
               LessonName %in% input[[gsub(" ", ".", kg)]]) %>%
        pull(LessonID)
      if(length(new.ids) > 0) {
        delete.sql = paste(delete.sql, "AND LessonID NOT IN ({new.ids*})")
      }
      delete.sql = glue_sql(delete.sql, .con = gnt.con)
      dbGetQuery(gnt.con, delete.sql)
      insert.sql = "INSERT INTO students_lessons
                    (StudentID, LessonID)
                    VALUES
                    ({student.id()}, {new.id})"
      for(new.id in new.ids) {
        if(!(new.id %in% knowledge.df()$LessonID)) {
          dbGetQuery(gnt.con, glue_sql(insert.sql, .con = gnt.con))
        }
      }
    }
    
    # Get the student's current knowledge
    knowledge.sql = glue_sql("SELECT LessonID
                                FROM students_lessons
                                WHERE StudentID = {student.id()}",
                             .con = gnt.con)
    knowledge.df(dbGetQuery(gnt.con, knowledge.sql))
    
  })
  
  # Get strings based on the student's knowledge
  observeEvent(knowledge.df(), {
    
    if(!is.null(knowledge.df())) {
      
      # Join lesson IDs to lesson names and groups
      known.lessons.df = knowledge.df() %>%
        inner_join(lessons.df, by = "LessonID")
      
      # Get cases the student knows
      allowed.case = c("X")
      for(cr in names(case.required)) {
        if(case.required[[cr]] %in% known.lessons.df$LessonName) {
          allowed.case = c(allowed.case, cr)
        }
      }
      
      # Get noun classes the student knows
      allowed.noun.class = c("X")
      for(ncr in names(noun.class.required)) {
        if(all(noun.class.required[[ncr]] %in% known.lessons.df$LessonName[known.lessons.df$LessonGroup == "Noun class"])) {
          allowed.noun.class = c(allowed.noun.class, ncr)
        }
      }
      
      # Get adjective classes the student knows
      allowed.adjective.class = c("X")
      for(acr in names(adjective.class.required)) {
        if(all(adjective.class.required[[acr]] %in% known.lessons.df$LessonName[known.lessons.df$LessonGroup == "Adjective class"])) {
          allowed.adjective.class = c(allowed.adjective.class, acr)
        }
      }
      
      # Get adjective degrees the student knows
      allowed.adjective.degree = c("X")
      for(adr in names(adjective.degree.required)) {
        if(adjective.degree.required[[adr]] %in% known.lessons.df$LessonName) {
          allowed.adjective.degree = c(allowed.adjective.degree, adr)
        }
      }
      
      # Get verb classes the student knows
      allowed.verb.class = c("X")
      for(vcr in names(verb.class.required)) {
        if(verb.class.required[[vcr]] %in% known.lessons.df$LessonName) {
          allowed.verb.class = c(allowed.verb.class, vcr)
        }
      }
      
      # Get tense-mood combinations the student knows
      allowed.tense.mood = c("X")
      for(tmr in names(tense.mood.required)) {
        if(tense.mood.required[[tmr]] %in% known.lessons.df$LessonName) {
          allowed.tense.mood = c(allowed.tense.mood, tmr)
        }
      }
      
      # Get voices the student knows
      allowed.voice = c("X")
      for(vr in names(voice.required)) {
        if(voice.required[[vr]] %in% known.lessons.df$LessonName) {
          allowed.voice = c(allowed.voice, vr)
        }
      }
      
      # Get other parts of speech the student knows
      allowed.other.pos = c("conj")
      for(opr in names(other.pos.required)) {
        if(all(other.pos.required[[opr]] %in% known.lessons.df$LessonName)) {
          allowed.other.pos = c(allowed.other.pos, opr)
        }
      }
      
      # Get relations the student DOESN'T know
      forbidden.relation = c("X")
      for(rr in names(relation.required)) {
        if(!all(relation.required[[rr]] %in% known.lessons.df$LessonName)) {
          forbidden.relation = c(forbidden.relation, rr)
        }
      }
      
      # Query the database for strings the student can read
      get.strings.sql = "WITH allowed_words AS
                              (SELECT SentenceID, SentencePosition
                               FROM words
                               WHERE (POS IN ({allowed.other.pos*})
                                      OR (POS = 'verb'
                                          AND VerbClassType IN ({allowed.verb.class*})
                                          AND CONCAT(Tense, '-', Mood) IN ({allowed.tense.mood*})
                                          AND Voice IN ({allowed.voice*}))
                                      OR (POS IN ('noun', 'reflexive pronoun',
                                                  'demonstrative pronoun',
                                                  'demonstrative pronoun with kai',
                                                  'interrogative pronoun',
                                                  'indefinite pronoun',
                                                  'relative pronoun')
                                          AND NounClassType IN ({allowed.noun.class*})
                                          AND (POS = 'noun'
                                               OR POS IN ({allowed.other.pos*})))
                                      OR (POS IN ('adj', 'pron')
                                          AND NounClassType IN ({allowed.adjective.class*})
                                          AND (Degree IS NULL
                                               OR Degree IN ({allowed.adjective.degree*}))))
                                     AND (COALESCE(NCase, 'X') IN ({allowed.case*}))),
                              forbidden_words AS
                              (SELECT words.SentenceID, words.SentencePosition
                               FROM words
                                    LEFT JOIN allowed_words
                                    ON words.SentenceID = allowed_words.SentenceID
                                       AND words.SentencePosition = allowed_words.SentencePosition
                               WHERE allowed_words.SentenceID IS NULL),
                              forbidden_relations AS
                              (SELECT SentenceID, FirstPos, LastPos
                               FROM relations
                               WHERE Relation IN ({forbidden.relation*})),
                              singleton_sentences AS
                              (SELECT SentenceID
                               FROM words
                               GROUP BY SentenceID
                               HAVING COUNT(*) = 1),
                              filtered_strings AS
                              (SELECT DISTINCT strings.Citation,
                                      strings.SentenceID, strings.Start,
                                      strings.Stop, strings.String
                               FROM strings
                                    LEFT JOIN forbidden_words
                                    ON strings.SentenceID = forbidden_words.SentenceID
                                       AND strings.Start <= forbidden_words.SentencePosition
                                       AND strings.Stop >= forbidden_words.SentencePosition
                                    LEFT JOIN forbidden_relations
                                    ON strings.SentenceID = forbidden_relations.SentenceID
                                       AND strings.Start <= forbidden_relations.FirstPos
                                       AND strings.Stop >= forbidden_relations.LastPos
                                    LEFT JOIN singleton_sentences
                                    ON strings.SentenceID = singleton_sentences.SentenceID
                               WHERE forbidden_words.SentenceID IS NULL
                                     AND forbidden_relations.SentenceID IS NULL
                                     AND (strings.Stop > strings.Start
                                          OR singleton_sentences.SentenceID IS NOT NULL)),
                              longest_strings AS
                              (SELECT filtered_strings.Citation,
                                      filtered_strings.SentenceID,
                                      filtered_strings.Start,
                                      filtered_strings.Stop,
                                      filtered_strings.String
                               FROM filtered_strings
                                    LEFT JOIN filtered_strings super_strings
                                    ON filtered_strings.SentenceID = super_strings.SentenceID
                                       AND filtered_strings.Start >= super_strings.Start
                                       AND filtered_strings.Stop <= super_strings.Stop
                                       AND NOT (filtered_strings.Start = super_strings.Start
                                                AND filtered_strings.Stop = super_strings.Stop)
                               WHERE super_strings.SentenceID IS NULL),
                              book_chapter_verse AS
                              (SELECT words.SentenceID,
                                      MIN(books.BookOrder) AS BookOrder,
                                      MIN(words.Chapter) AS Chapter,
                                      MIN(words.Verse) AS Verse
                               FROM words
                                    JOIN books
                                    ON words.Book = books.Book
                               GROUP BY words.SentenceID)
                         SELECT ls.Citation, bcv.BookOrder, bcv.Chapter,
                                bcv.Verse, ls.SentenceID, ls.Start, ls.Stop,
                                ls.String,
                                CONCAT(w.Tense, '-', w.Mood) AS TenseMood,
                                w.Voice, w.NounClassType, w.VerbClassType,
                                r.Relation
                         FROM longest_strings ls
                              JOIN book_chapter_verse bcv
                              ON ls.SentenceID = bcv.SentenceID
                              JOIN words w
                              ON ls.SentenceID = w.SentenceID
                                 AND ls.Start <= w.SentencePosition
                                 AND ls.Stop >= w.SentencePosition
                              LEFT JOIN (SELECT DISTINCT longest_strings.SentenceID,
                                                longest_strings.Start,
                                                longest_strings.Stop,
                                                relations.DependentPos,
                                                relations.Relation
                                         FROM relations
                                              JOIN longest_strings
                                              ON relations.SentenceID = longest_strings.SentenceID
                                                 AND relations.HeadPos >= longest_strings.Start
                                                 AND relations.HeadPos <= longest_strings.Stop
                                         WHERE relations.Relation NOT IN
                                               ('appositive', 'conjunct, chain',
                                               'determiner', 'entitled', 'gap',
                                               'interjection, vocative', 'name',
                                               'negation, double',
                                               'parenthetical', 'particle',
                                               'second-position clitic',
                                               'subject of small clause',
                                               'title')) r
                              ON ls.SentenceID = r.SentenceID
                                 AND ls.Start = r.Start
                                 AND ls.Stop = r.Stop
                                 AND w.SentencePosition = r.DependentPos"
      get.strings.sql = glue_sql(get.strings.sql, .con = gnt.con)
      everything.df = dbGetQuery(gnt.con, get.strings.sql)
      everything.df %>%
        dplyr::select(Citation, BookOrder, Chapter, Verse, SentenceID, Start,
                      Stop, String) %>%
        distinct() %>%
        all.strings.df()
      everything.df %>%
        dplyr::select(SentenceID, Start, Stop, TenseMood, Voice, NounClassType,
                      VerbClassType) %>%
        pivot_longer(cols = -c("SentenceID", "Start", "Stop"),
                     names_to = "property") %>%
        distinct() %>%
        inner_join(word.property.names.df, by = c("property", "value")) %>%
        all.word.properties.df()
      everything.df %>%
        filter(!is.na(Relation)) %>%
        dplyr::select(SentenceID, Start, Stop, Relation) %>%
        distinct() %>%
        inner_join(relation.names.df, by = c("Relation" = "relation")) %>%
        all.relations.df()
      
    }
    
  })
  
  # Refresh possible excerpt filters
  observeEvent(all.word.properties.df(), {
    example.choices = c("[everything]",
                        split(all.word.properties.df()$pretty.value, all.word.properties.df()$pretty.property),
                        list(`Syntactic structure` = sort(all.relations.df()$pretty.relation)))
    updateSelectInput(session = session, inputId = "string.examples",
                      choices = example.choices)
  })
  
  # Refresh sample of strings
  observeEvent(
    {
      input$refresh.strings
      all.strings.df()
    },
    {
      temp.df = all.strings.df()
      if(input$string.examples != "[everything]") {
        if(input$string.examples %in% all.relations.df()$pretty.relation) {
          temp.df = temp.df %>%
            inner_join(all.relations.df() %>%
                         filter(pretty.relation == input$string.examples) %>%
                         dplyr::select(SentenceID, Start, Stop) %>%
                         distinct(),
                       by = c("SentenceID", "Start", "Stop"))
        } else if(input$string.examples %in% all.word.properties.df()$pretty.value) {
          temp.df = temp.df %>%
            inner_join(all.word.properties.df() %>%
                         filter(pretty.value == input$string.examples) %>%
                         dplyr::select(SentenceID, Start, Stop) %>%
                         distinct(),
                       by = c("SentenceID", "Start", "Stop"))
        }
      }
      temp.df %>%
        slice_sample(n = input$string.count) %>%
        sample.strings.df()
    }
  )
  
  # Render strings
  output$show.strings = renderDT({
    if(is.null(sample.strings.df())) {
      sample.strings.df()
    } else {
      sample.strings.df() %>%
        arrange(BookOrder, Chapter, Verse) %>%
        dplyr::select(Citation, String) %>%
        datatable(options = list(paging = F,
                                 searching = F,
                                 stripe = F,
                                 ordering = F,
                                 info = F,
                                 headerCallback = JS(
                                   "function(thead, data, start, end, display){",
                                   "  $(thead).remove();",
                                   "}")),
                  rownames = F) %>%
        formatStyle(columns = c("Citation"), fontWeight = "bold", width = "25%")
    }
  })
  
  # Disconnect from the database when we're done
  session$onSessionEnded(function(){
    dbDisconnect(gnt.con)
  })
  
}

#### Run ####

# Run the application 
shinyApp(ui = ui, server = server)
