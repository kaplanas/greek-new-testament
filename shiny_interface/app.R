library(shiny)
library(tidyverse)
library(bslib)
library(DT)
library(paws)
library(htmltools)
library(shinyBS)

#### Get starting data ####

# List of lessons
lessons.df = read.csv("lessons.csv") %>%
  mutate(AttributeName = paste("L", ColumnName, sep = "_"))

# Pretty names for properties to filter on
filter.property.names.df = read.csv("filter_property_names.csv")

# Words and lemmas
lemmas.df = read.csv("lemmas.csv")
words.df = read.csv("words.csv")

# Strings
strings.df = read.csv("strings.csv")
strings.lessons.df = read.csv("strings_lessons.csv")
strings.properties.df = read.csv("strings_properties.csv")

#### Code for tooltips ####
makeCheckboxTooltip <- function(checkboxValue, tooltip){
  tags$script(HTML(paste0("$(document).ready(function() {
                             var inputElements = document.getElementsByTagName('input');
                             for(var i = 0; i < inputElements.length; i++) {
                               var input = inputElements[i];
                               if(input.getAttribute('value') == '", checkboxValue, "' && input.getAttribute('value') != 'null') {
                                 input.parentElement.setAttribute('data-toggle', 'tooltip');
                                 input.parentElement.setAttribute('title', '", tooltip, "');
                               };
                             }
                           });")))
}

#### UI ####

# Page title
page.title = "New Testament Greek"

# Login page
login.page = nav_panel(
  title = "Log in",
  tabsetPanel(
    tabPanel("Log in",
             tagQuery(textInput("existing.email", "Email"))$find("input")$addAttrs("autocomplete" = "off")$allTags(),
             passwordInput("existing.password", "Password (min 8 characters)"),
             actionButton("log.in", label = "Log in")),
    tabPanel("Register",
             textInput("new.email", "Email"),
             actionButton("register", label = "Register")),
    tabPanel("Forgot password",
             textInput("forgotten.email", "Email"),
             actionButton("forgot.password", label = "Get verification code")),
    tabPanel("Reset password",
             textInput("reset.email", "Email"),
             passwordInput("reset.code", "Verification code"),
             passwordInput("reset.new.password", "New password (min 8 characters)"),
             actionButton("reset.password", label = "Reset password")),
    tabPanel("Change password",
             textInput("change.email", "Email"),
             passwordInput("change.old.password", "Old password"),
             passwordInput("change.new.password", "New password (min 8 characters)"),
             actionButton("change.password", label = "Change password"))
  )
)

# Page of user's knowledge
knowledge.groups = map(
  set_names(unique(lessons.df$LessonGroup)),
  function(lg) {
    sub.lessons.df = lessons.df %>%
      filter(LessonGroup == lg)
    tagQuery(checkboxGroupInput(gsub(" ", ".", lg),
                                lg,
                                set_names(sub.lessons.df$AttributeName,
                                          sub.lessons.df$LessonName)))$find("input")$addAttrs("autocomplete" = "off")$allTags()
  }
)
knowledge.page = nav_panel(title = "Current knowledge",
                           actionButton("update.knowledge",
                                        "Save changes"),
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
                           ),
                           uiOutput("tooltips"))

# Page with excerpts.
string.page = nav_panel(title = "Excerpts",
                        layout_columns(
                          layout_columns(
                            actionButton("refresh.strings", "Refresh"),
                            numericInput("string.count",
                                         "Number of excerpts to show:",
                                         value = 10),
                            radioButtons("sample.by",
                                         "Sample:",
                                         choices = list("Randomly" = "random",
                                                        "Longest first" = "longest",
                                                        "Shortest first" = "shortest")),
                            selectizeInput("string.examples",
                                           "Include examples of:",
                                           choices = list(`Everything` = list("[everything]" = "[everything]"))),
                            tags$head(tags$style(HTML(".selectize-dropdown-content{max-height: 100% !important; height: 100% !important;}}"))),
                            col_widths = c(11, -1),
                            fill = F
                          ),
                          DTOutput("show.strings"),
                          col_widths = c(3, 9)
                        ))

# Define UI
ui <- page_navbar(
  title = page.title,
  shinyjs::useShinyjs(),
  tags$head(HTML("<script type='text/javascript' src='sbs/shinyBS.js'></script>")),
  login.page,
  knowledge.page,
  string.page,
  nav_panel(title = "Lexicon for excerpts", DTOutput("lexicon")),
  nav_panel(title = "About", includeHTML("about.html")),
  useBusyIndicators()
)

#### Server ####

# Define server logic
server <- function(input, output, session) {
  
  # Get ready to authenticate with Cognito
  Sys.setenv(AWS_PROFILE = "greek_shiny_server_test")
  svc = cognitoidentityprovider()
  user.pool.id = "us-west-2_zgB6VtmdZ"
  user.pool.client.id = "3dtao8kuc335orn7fimfvk8qlb"
  
  # Database connection
  db = dynamodb()
  
  # Student data
  knowledge.df = reactiveVal(NULL)
  known.strings.df = reactiveVal(NULL)
  known.filter.properties.df = reactiveVal(NULL)
  sample.strings.df = reactiveVal(NULL)
  sample.lexicon.df = reactiveVal(NULL)
  
  # Tooltips
  output$tooltips <-   renderUI({
    pmap(
      lessons.df %>% dplyr::select(AttributeName, Tooltip),
      function(AttributeName, Tooltip) {
        makeCheckboxTooltip(checkboxValue = AttributeName, tooltip = Tooltip)
      }
    )
  })
  
  # If the user forgot his or her password, start the reset process
  observeEvent(input$forgot.password, {
    tryCatch(
      {
        admin.reset.result = svc$admin_reset_user_password(UserPoolId = user.pool.id,
                                                           Username = input$forgotten.email)
        showNotification("Check your email for a verification code",
                         type = "warning")
      },
      error = function(err) {
        cat(file = stderr(), err$message)
        showNotification("Sending verification code failed", type = "error")
      }
    )
  })
  
  # When the user attempts to complete the password reset process, do that
  observeEvent(input$reset.password, {
    tryCatch(
      {
        reset.result = svc$confirm_forgot_password(ClientId = user.pool.client.id,
                                                   Username = input$reset.email,
                                                   ConfirmationCode = input$reset.code,
                                                   Password = input$reset.new.password)
        showNotification("Password reset", type = "message")
      },
      error = function(err) {
        cat(file = stderr(), err$message)
        showNotification("Password reset failed", type = "error")
      }
    )
  })
  
  # When the user registers, create a new user
  observeEvent(input$register, {
    tryCatch(
      {
        tryCatch(
          {
            create.result = svc$admin_create_user(UserPoolId = user.pool.id,
                                                  Username = input$new.email)
            showNotification("Check your email for your temporary password",
                             type = "message")
          },
          error = function(err) {
            cat(file = stderr(), err$message)
            if(grepl("already exists", err$message)) {
              showNotifiation("Account already exists", type = "error")
            } else {
              showNotification("Registration failed", type = "error")
            }
          }
        )
        svc$admin_update_user_attributes(UserPoolId = user.pool.id,
                                         Username = input$new.email,
                                         UserAttributes = list(list(Name = "email_verified",
                                                                    Value = "true")))
        db$put_item(TableName = "nt_users",
                    Item = list(username = list(S = input$new.email),
                                L_nom = list(BOOL = TRUE),
                                L_eimi = list(BOOL = TRUE),
                                L_pres_ind = list(BOOL = TRUE),
                                L_act = list(BOOL = TRUE),
                                L_p_pers = list(BOOL = TRUE)))
      },
      error = function(err) {
        cat(file = stderr(), err$message)
      }
    )
  })
  
  # When the user changes a password, do that
  observeEvent(input$change.password, {
    tryCatch(
      {
        auth.result = svc$initiate_auth(AuthFlow = "USER_PASSWORD_AUTH",
                                        AuthParameters = list(USERNAME = input$change.email,
                                                              PASSWORD = input$change.old.password),
                                        ClientId = user.pool.client.id)
        if(length(auth.result$AuthenticationResult$AccessToken) > 0) {
          change.result = svc$change_password(PreviousPassword = input$change.old.password,
                                              ProposedPassword = input$change.new.password,
                                              AccessToken = auth.result$AuthenticationResult$AccessToken)
          showNotification("Password changed", type = "message")
        }
        else if(auth.result$ChallengeName == "NEW_PASSWORD_REQUIRED") {
          change.result = svc$admin_set_user_password(UserPoolId = user.pool.id,
                                                      Username = input$change.email,
                                                      Password = input$change.new.password,
                                                      Permanent = T)
          showNotification("Password changed", type = "message")
        }
      },
      error = function(err) {
        cat(file = stderr(), err$message)
        showNotification("Password change failed", type = "error")
      }
    )
  })

  # When the user attempts to log in, attempt to create a connection and
  # get the user's data
  observeEvent(input$log.in, {

    # Is the user authorized?
    authorized.user = F

    # Authenticate as this user
    tryCatch(
      {
        auth.result = svc$initiate_auth(AuthFlow = "USER_PASSWORD_AUTH",
                                        AuthParameters = list(USERNAME = input$existing.email,
                                                              PASSWORD = input$existing.password),
                                        ClientId = user.pool.client.id)
        if(length(auth.result$AuthenticationResult$AccessToken) > 0) {
          authorized.user = T
          showNotification("Login successful", type = "message")
        } else {
          cat(file = stderr(), "login failed for some reason")
          cat(file = stderr(), paste(auth.result, collapse = "\n"))
          showNotification("Login failed", type = "error")
        }
      },
      error = function(err) {
        cat(file = stderr(), err$message)
        showNotification(err$message, type = "error")
      }
    )

    # If we connected successfully, get some data
    if(authorized.user) {
      
      # Get the student's current knowledge.
      knowledge.df = db$get_item(TableName = "nt_users",
                                 Key = list(username = list(S = input$existing.email)),
                                 ProjectionExpression = paste(lessons.df$AttributeName,
                                                              collapse = ","))$Item %>%
        map_dfr(function(col) { data.frame(known = col$BOOL) },
                .id = "AttributeName") %>%
        knowledge.df()

      # Update knowledge panel with student's current knowledge
      if(nrow(knowledge.df()) > 0) {
        for(cgi in names(knowledge.groups)) {
          updateCheckboxGroupInput(session, inputId = gsub(" ", ".", cgi),
                                   selected = knowledge.df()$AttributeName)
        }
      }
      else {
        for(cgi in names(knowledge.groups)) {
          updateCheckboxGroupInput(session, inputId = gsub(" ", ".", cgi),
                                   selected = c())
        }
      }

    }

  })

  # Update the student's knowledge in the database when the user clicks the
  # "save" button
  observeEvent(input$update.knowledge, {

    # Update the student's new knowledge
    known.cols = do.call(
      "c",
      lapply(names(knowledge.groups),
             function(kg) { input[[gsub(" ", ".", kg)]] })
    )
    add.cols = setdiff(known.cols, knowledge.df()$AttributeName)
    remove.cols = setdiff(knowledge.df()$AttributeName, known.cols)
    update.exp = ""
    expr.attr.vals = list()
    if(length(add.cols) > 0) {
      update.exp = paste("SET", paste(paste(add.cols, "= :true"),
                                      collapse = ", "))
      expr.attr.vals = list(`:true` = list(BOOL = T))
    }
    if(length(add.cols) > 0 & length(remove.cols) > 0) {
      update.exp = paste(update.exp, " ", sep = "")
    }
    if(length(remove.cols) > 0) {
      update.exp = paste(update.exp,
                         paste("REMOVE", paste(remove.cols, collapse = ", ")),
                         sep = "")
    }
    db$update_item(TableName = "nt_users",
                   Key = list(username = list(S = input$existing.email)),
                   UpdateExpression = update.exp,
                   ExpressionAttributeValues = expr.attr.vals)
    
    # Get the student's current knowledge.
    knowledge.df = db$get_item(TableName = "nt_users",
                               Key = list(username = list(S = input$existing.email)),
                               ProjectionExpression = paste(lessons.df$AttributeName,
                                                            collapse = ","))$Item %>%
      map_dfr(function(col) { data.frame(known = col$BOOL) },
              .id = "AttributeName") %>%
      knowledge.df()

  })

  # Get strings based on the student's knowledge
  observeEvent(knowledge.df(), {

    if(!is.null(knowledge.df()) & nrow(knowledge.df()) > 0) {
      
      # Get known strings
      strings.df %>%
        anti_join(lessons.df %>%
                    filter(!(AttributeName %in% knowledge.df()$AttributeName)) %>%
                    inner_join(strings.lessons.df, by = "LessonID"),
                  by = c("SentenceID", "Start", "Stop")) %>%
        group_by(SentenceID, Start) %>%
        filter(Stop == max(Stop)) %>%
        ungroup() %>%
        group_by(SentenceID, Stop) %>%
        filter(Start == min(Start)) %>%
        ungroup() %>%
        mutate(n.words = str_count(String, " ") + 1) %>%
        known.strings.df()
      
      # Get properties of strings the student might want to filter on
      strings.properties.df %>%
        semi_join(known.strings.df(), by = c("SentenceID", "Start", "Stop")) %>%
        dplyr::select(SentenceID, Start, Stop, AttributeName) %>%
        distinct() %>%
        known.filter.properties.df()

    } else if(!is.null(knowledge.df())) {
      known.strings.df(data.frame(SentenceID = c(), Start = c(), Stop = c(),
                                  BookOrder = c(), Chapter = c(), Verse = c(),
                                  Citation = c(), String = c(), n.words = c()))
      known.filter.properties.df(data.frame(SentenceID = c(), Start = c(),
                                            Stop = c(), AttributeName = c()))
    }

  })

  # Refresh possible excerpt filters
  observeEvent(known.filter.properties.df(), {
    if(nrow(known.filter.properties.df()) > 0) {
      temp.df = known.filter.properties.df() %>%
        inner_join(filter.property.names.df, by = "AttributeName") %>%
        dplyr::select(AttributeName, pretty.value, pretty.property) %>%
        distinct() %>%
        arrange(pretty.property, pretty.value)
      example.choices = c(list(`Everything` = list("[everything]" = "[everything]")),
                          map(set_names(unique(temp.df$pretty.property)),
                              function(pp) {
                                pretty.values.df = temp.df %>%
                                  filter(pretty.property == pp) %>%
                                  dplyr::select(AttributeName, pretty.value)
                                map(set_names(pretty.values.df$pretty.value),
                                    function(pv) {
                                      pretty.values.df$AttributeName[pretty.values.df$pretty.value == pv]
                                    })
                              }))
    } else {
      example.choices = c(list(`Everything` = list("[everything]" = "[everything]")))
    }
    updateSelectizeInput(session = session, inputId = "string.examples",
                         choices = example.choices)
  })

  # Refresh sample of strings
  observeEvent(
    {
      input$refresh.strings
      known.strings.df()
    },
    {
      temp.df = known.strings.df()
      if(nrow(temp.df) > 0) {
        if(input$string.examples != "[everything]") {
          example.filter = input$string.examples
          if(grepl("^c[(]", example.filter)) {
            example.filter = eval(parse(text = input$string.examples))
          }
          known.attributes = c()
          if(nrow(known.filter.properties.df()) > 0) {
            known.attributes = known.filter.properties.df()$AttributeName
          }
          if(any(example.filter %in% known.attributes)) {
            temp.df = temp.df %>%
              inner_join(known.filter.properties.df() %>%
                           filter(AttributeName %in% example.filter) %>%
                           dplyr::select(SentenceID, Start, Stop) %>%
                           distinct(),
                         by = c("SentenceID", "Start", "Stop"))
          }
        }
        if(input$sample.by == "random") {
          temp.df = temp.df %>%
            slice_sample(n = input$string.count) %>%
            arrange(BookOrder, Chapter, Verse)
        }
        else if(input$sample.by == "longest") {
          temp.df = temp.df %>%
            mutate(random.order = runif(n())) %>%
            arrange(desc(n.words), random.order) %>%
            slice_head(n = input$string.count) %>%
            arrange(desc(n.words), BookOrder, Chapter, Verse)
        }
        else if(input$sample.by == "shortest") {
          temp.df = temp.df %>%
            mutate(random.order = runif(n())) %>%
            arrange(n.words, random.order) %>%
            slice_head(n = input$string.count) %>%
            arrange(n.words, BookOrder, Chapter, Verse)
        }
      }
      sample.strings.df(temp.df)
      if(nrow(temp.df) > 0) {
        temp.df %>%
          inner_join(words.df,
                     by = join_by(SentenceID, Start <= SentencePosition,
                                  Stop >= SentencePosition)) %>%
          inner_join(lemmas.df, by = c("Lemma", "POS")) %>%
          mutate(PrincipalParts = if_else(POS == "noun",
                                          paste(PrincipalParts, " <i>(",
                                                case_match(Gender,
                                                           "masculine" ~ "masc.",
                                                           "feminine" ~ "fem.",
                                                           "neuter" ~ "neut."),
                                                ")</i>", sep = ""),
                                          PrincipalParts)) %>%
          dplyr::select(Lemma, LemmaSort, POS, PrincipalParts,
                        ShortDefinition) %>%
          distinct() %>%
          sample.lexicon.df()
      } else {
        sample.lexicon.df(NULL)
      }
    }
  )

  # Render strings
  output$show.strings = renderDT({
    if(is.null(sample.strings.df()) | nrow(sample.strings.df()) == 0) {
      sample.strings.df()
    } else {
      sample.strings.df() %>%
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

  # Render lexicon
  output$lexicon = renderDT({
    if(is.null(sample.lexicon.df())) {
      NULL
    } else {
      sample.lexicon.df() %>%
        arrange(LemmaSort) %>%
        dplyr::select(Lemma, PrincipalParts, ShortDefinition) %>%
        datatable(options = list(paging = F,
                                 searching = F,
                                 stripe = F,
                                 ordering = F,
                                 info = F,
                                 headerCallback = JS(
                                   "function(thead, data, start, end, display){",
                                   "  $(thead).remove();",
                                   "}")),
                  rownames = F, escape = F) %>%
        formatStyle(columns = c("Lemma"), fontWeight = "bold", width = "15%")
    }
  })
  
}

#### Run ####

# Run the application 
shinyApp(ui = ui, server = server)
