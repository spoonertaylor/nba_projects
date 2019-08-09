
shinyUI(fluidPage(
  tags$head(includeCSS("www/style.css")),
  # Application title
  titlePanel("NBA Player Projection"),
  # Sidebar with a slider input for number of bins 
  column(width = 3,
    fluidRow(
      sidebarPanel(width = 12,
         selectInput("player_id",
                          "Player:",
                          choices = setNames(player_select$bbref_id, player_select$player_select_col),
                          selected = setNames(player_select[rand_row, "bbref_id"], player_select[rand_row, "player_select_col"]),
                          multiple = FALSE)
      )),
    fluidRow(
      h2(textOutput("player_name"), id = "player_name_cont"),
      h4(textOutput("player_position"), id = "player_info_cont"),
      h4(htmlOutput("player_age"), id = "player_info_cont"),
      h4(htmlOutput("player_measurement"), id = "player_info_cont"),
      tableOutput("player_salary"),
      p(HTML(paste0("<text style='color:red;font-size11px;font-style:italic'>Player Option</text>/",
                    "<text style='color:blue;font-size11px;font-style:italic'>Team Option</text>/",
                    "<text style='color:hotpink;font-size11px;font-style:italic'>Early Termination</text>")),
        class = "contract_info")
    )
    ),
    column(width = 8,
       plotOutput("player_projection"),
       tableOutput("player_table")
    )
))
