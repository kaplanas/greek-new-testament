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
                        "SELECT LessonName, LessonGroup
                         FROM lessons
                         ORDER BY DisplayOrder")

# Lessons required for noun classes
noun.class.required = list(
  "second declension" = c("Second declension"),
  "first declension" = c("First declension"),
  "first declension with hs" = c("Second declension", "First declension"),
  "first/second declension" = c("Second declension", "First declension"),
  "third declension, consonant stem" = c("Third declension"),
  "third declension, vowel stem" = c("Third declension"),
  "first/second declension; third declension, consonant stem" = c("Second declension", "First declension", "Third declension"),
  "Ihsous" = c("Ἰησοῦς"),
  "irregular" = c("Irregular"),
  "undeclined" = c("Undeclined")
)
adjective.degree.required = list(
  "comparative" = "Comparatives",
  "superlative" = "Superlatives"
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

# Lessons required for tense and mood
tense.mood.required = list(
  "present-indicative" = "Present indicative",
  "future-indicative" = "Future indicative",
  "imperfect-indicative" = "Imperfect indicative",
  "aorist-indicative" = "Aorist indicative",
  "present-infinitive" = "Present infinitive",
  "future-infinitive" = "Future infinitive",
  "aorist-infinitive" = "Aorist infinitive"
)

# Lessons required for voice
voice.required = list(
  "active" = "Active",
  "middle" = "Middle",
  "passive" = "Passive"
)

# Lessons required for various parts of speech
other.pos.required = list(
  "personal pronoun" = c("Personal pronouns"),
  "personal pronoun with kai" = c("Personal pronouns", "Coordinating conjunctions"),
  "reflexive pronoun" = c("Reflexive pronouns"),
  "demonstrative pronoun" = c("Demonstrative pronouns"),
  "demonstrative pronoun with kai" = c("Demonstrative pronouns", "Coordinating conjunctions"),
  "interrogative pronoun" = c("Interrogative pronouns"),
  "indefinite pronoun" = c("Indefinite pronouns")
)

# Lessons required for relations
relation.required = list(
  "subject" = c("Subjects"),
  "subject of implicit speech" = c("Subjects"),
  "subject of infinitive" = c("Subjects"),
  "subject of infinitive, attraction" = c("Subjects"),
  "subject of participle" = c("Subjects", "Participles"),
  "subject of small clause" = c("Subjects"),
  "subject of verbless predicate" = c("Subjects"),
  "subject, attraction" = c("Subjects", "Relative clauses"),
  "subject, irregular agreement" = c("Subjects"),
  "subject, neuter plural" = c("Subjects"),
  "subject, neuter plural, regular agreement" = c("Subjects"),
  "direct object" = c("Direct objects"),
  "direct object, attraction" = c("Direct objects"),
  "indirect object" = c("Indirect objects"),
  "indirect object, attraction" = c("Indirect objects"),
  "predicate, nominal" = c("Predicates"),
  "predicate, non-nominal" = c("Predicates"),
  "genitive, relation" = c("Genitive"),
  "genitive, other" = c("Genitive"),
  "genitive, body part" = c("Genitive"),
  "genitive, subject" = c("Genitive"),
  "genitive, possession" = c("Genitive"),
  "genitive, object" = c("Genitive"),
  "genitive, part-whole" = c("Genitive"),
  "genitive, source" = c("Genitive"),
  "genitive, characterized by" = c("Genitive"),
  "genitive, location" = c("Genitive"),
  "genitive, specification" = c("Genitive"),
  "genitive, material" = c("Genitive"),
  "genitive, time" = c("Genitive"),
  "genitive, comparative" = c("Genitive", "Comparatives"),
  "genitive, property" = c("Genitive"),
  "genitive, about" = c("Genitive"),
  "genitive, contents" = c("Genitive"),
  "genitive, son of" = c("Genitive"),
  "genitive, amount" = c("Genitive"),
  "dative, other" = c("Dative"),
  "dative, instrument" = c("Dative"),
  "dative, benefit" = c("Dative"),
  "dative, time" = c("Dative"),
  "dative, manner" = c("Dative"),
  "dative, possession" = c("Dative"),
  "dative, agent" = c("Dative"),
  "dative, cognate of verb" = c("Dative"),
  "dative, Hebrew infinitive construct" = c("Dative"),
  "accusative, other" = c("Accusative"),
  "accusative, time" = c("Accusative"),
  "accusative, amount" = c("Accusative"),
  "accusative, manner" = c("Accusative"),
  "accusative, cognate of verb" = c("Accusative"),
  "interjection, vocative" = c("Vocative"),
  "conjunct" = c("Coordinating conjunctions"),
  "conjunct, main" = c("Subordinating conjunctions"),
  "conjunct, subordinate" = c("Subordinating conjunctions"),
  "conjunct, μέν δέ" = c("Μὲν δέ"),
  "conjunct, ὡς, clause" = c("Ὡς"),
  "conjunct, ὡς, non-clause" = c("Ὡς"),
  "conjunct, ὡς, other" = c("Ὡς"),
  "conjunct, ἤ" = c("Comparatives"),
  "comparative" = c("Comparatives"),
  "second-position clitic" = c("Second-position clitics")
)

#### UI ####

# Page title
page.title = "New Testament Greek"

# Login page
login.page = nav_panel("Log in",
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
knowledge.page = nav_panel("Current knowledge",
                           actionButton("update.knowledge", "Save changes"),
                           layout_columns(
                             card(card_header(class = "bg-dark", "Nouns and adjectives"),
                                  knowledge.groups[["Noun class"]],
                                  knowledge.groups[["Adjective forms"]]),
                             card(card_header(class = "bg-dark", "Verbs"),
                                  knowledge.groups[["Verb class"]],
                                  knowledge.groups[["Tense and mood"]],
                                  knowledge.groups[["Voice"]]),
                             card(card_header(class = "bg-dark", "Other"),
                                  knowledge.groups[["Other parts of speech"]])
                           ),
                           layout_columns(
                             card(card_header(class = "bg-dark", "Relations"),
                                  knowledge.groups[["Arguments of verbs"]],
                                  knowledge.groups[["Uses of cases"]],
                                  knowledge.groups[["Conjunction"]])
                           ))
string.page = nav_panel("Excerpts",
                        DTOutput("show.strings"))

# Define UI
ui <- page_navbar(
  useBusyIndicators(),
  title = page.title,
  login.page,
  knowledge.page,
  string.page
)

#### Server ####

# Define server logic
server <- function(input, output, session) {
  
  # Student data
  student.id = reactiveVal(NULL)
  knowledge.df = reactiveVal(NULL)
  strings.df = reactiveVal(NULL)
  
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
      knowledge.sql = glue_sql("SELECT LessonName
                                FROM students_lessons
                                WHERE StudentID = {student.id()}",
                               .con = gnt.con)
      knowledge.df(dbGetQuery(gnt.con, knowledge.sql))
      
      # Update knowledge panel with student's current knowledge
      for(cgi in names(knowledge.groups)) {
        updateCheckboxGroupInput(session, inputId = gsub(" ", ".", cgi),
                                 selected = lessons.df %>%
                                   filter(LessonGroup == cgi) %>%
                                   inner_join(knowledge.df(), by = "LessonName") %>%
                                   pull(LessonName))
      }
      
    }
    
  })
  
  # Update the student's knowledge in the database when the user clicks the
  # "save" button
  observeEvent(input$update.knowledge, {
    
    # Update the student's new knowledge
    for(cgi in names(knowledge.groups)) {
      delete.sql = "DELETE FROM students_lessons
                    WHERE StudentID = {student.id()}
                          AND LessonName IN (SELECT LessonName
                                             FROM lessons
                                             WHERE LessonGroup = {cgi})"
      new.vals = input[[gsub(" ", ".", cgi)]]
      if(length(new.vals) > 0) {
        delete.sql = paste(delete.sql, "AND LessonName NOT IN ({new.vals*})")
      }
      delete.sql = glue_sql(delete.sql, .con = gnt.con)
      dbGetQuery(gnt.con, delete.sql)
      insert.sql = "INSERT INTO students_lessons
                    (StudentID, LessonName)
                    VALUES
                    ({student.id()}, {new.val})"
      for(new.val in new.vals) {
        if(!(new.val %in% knowledge.df()$LessonName)) {
          dbGetQuery(gnt.con, glue_sql(insert.sql, .con = gnt.con))
        }
      }
    }
    
    # Get the student's current knowledge
    knowledge.sql = glue_sql("SELECT LessonName
                                FROM students_lessons
                                WHERE StudentID = {student.id()}",
                             .con = gnt.con)
    knowledge.df(dbGetQuery(gnt.con, knowledge.sql))
    
  })
  
  # Get strings based on the student's knowledge
  observeEvent(knowledge.df(), {
    
    if(!is.null(knowledge.df())) {
      
      # Get noun classes the student knows
      allowed.noun.class = c("X")
      for(ncr in names(noun.class.required)) {
        if(all(noun.class.required[[ncr]] %in% knowledge.df()$LessonName)) {
          allowed.noun.class = c(allowed.noun.class, ncr)
        }
      }
      
      # Get adjective degrees the student knows
      allowed.adjective.degree = c("X")
      for(adr in names(adjective.degree.required)) {
        if(adjective.degree.required[[adr]] %in% knowledge.df()$LessonName) {
          allowed.adjective.degree = c(allowed.adjective.degree, adr)
        }
      }
      
      # Get verb classes the student knows
      allowed.verb.class = c("X")
      for(vcr in names(verb.class.required)) {
        if(verb.class.required[[vcr]] %in% knowledge.df()$LessonName) {
          allowed.verb.class = c(allowed.verb.class, vcr)
        }
      }
      
      # Get tense-mood combinations the student knows
      allowed.tense.mood = c("X")
      for(tmr in names(tense.mood.required)) {
        if(tense.mood.required[[tmr]] %in% knowledge.df()$LessonName) {
          allowed.tense.mood = c(allowed.tense.mood, tmr)
        }
      }
      
      # Get voices the student knows
      allowed.voice = c("X")
      for(vr in names(voice.required)) {
        if(voice.required[[vr]] %in% knowledge.df()$LessonName) {
          allowed.voice = c(allowed.voice, vr)
        }
      }
      
      # Get other parts of speech the student knows
      allowed.other.pos = c("conj")
      for(opr in names(other.pos.required)) {
        if(all(other.pos.required[[opr]] %in% knowledge.df()$LessonName)) {
          allowed.other.pos = c(allowed.other.pos, opr)
        }
      }
      print(allowed.other.pos)
      
      # Get relations the student knows
      allowed.relation = c("conjunct, chain", "name", "title", "entitled")
      for(rr in names(relation.required)) {
        if(all(relation.required[[rr]] %in% knowledge.df()$LessonName)) {
          allowed.relation = c(allowed.relation, rr)
        }
      }
      
      # Query the database for strings the student can read
      get.strings.sql = "WITH allowed_words AS
                              (SELECT SentenceID, SentencePosition
                               FROM words
                               WHERE POS IN ({allowed.other.pos*})
                                     OR (POS = 'verb'
                                         AND VerbClassType IN ({allowed.verb.class*})
                                         AND CONCAT(Tense, '-', Mood) IN ({allowed.tense.mood*})
                                         AND Voice IN ({allowed.voice*}))
                                     OR (POS IN ('noun', 'adj',
                                                 'reflexive pronoun',
                                                 'demonstrative pronoun',
                                                 'demonstrative pronoun with kai',
                                                 'interrogative pronoun',
                                                 'indefinite pronoun',
                                                 'relative pronoun')
                                         AND NounClassType IN ({allowed.noun.class*})
                                         AND (Degree IS NULL
                                              OR Degree IN ({allowed.adjective.degree*}))
                                         AND (POS IN ('noun', 'adj')
                                              OR POS IN ({allowed.other.pos*})))),
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
                               WHERE Relation NOT IN ({allowed.relation*})),
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
                                bcv.Verse, ls.String
                         FROM longest_strings ls
                              JOIN book_chapter_verse bcv
                              ON ls.SentenceID = bcv.SentenceID"
      get.strings.sql = glue_sql(get.strings.sql, .con = gnt.con)
      strings.df(dbGetQuery(gnt.con, get.strings.sql))
      
    }
    
  })
  
  # Render strings
  output$show.strings = renderDT({
    if(is.null(strings.df())) {
      strings.df()
    } else {
      strings.df() %>%
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
