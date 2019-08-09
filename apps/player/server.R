source('global.R')
# Define server logic required to draw a histogram
shinyServer(function(input, output, session) {
  # * Data ----
  player_projection_df <- reactive({
    projection %>% filter(bbref_id == input$player_id)
  }) 
  # 
  # player_select_df <- reactive({
  #   player_select %>% filter(bbref_id == input$player_id)
  # })
  # 
  player_stats <- reactive({
    stats_percentiles %>% filter(bbref_id == input$player_id) %>%
      select(-bbref_id)
  })
  
  player_info_df <- reactive({
    player_info %>% filter(bbref_id == input$player_id) %>% 
      select(-bbref_id)
  })
  
  player_salary <- reactive({
    salary %>% filter(bbref_id == input$player_id) %>%
      select(-bbref_id)
  })
  
  # * Output ----
  # ** Player's Name ----
  output$player_name <- renderText({
    player_info_df()$player_name
  })
  
  # ** Player's Position ----
  output$player_position <- renderText({
    first_position = player_info_df()$position_minutes
    position_num = player_info_df()$position_numeric
    advanced_position = player_info_df()$advanced_position_cluster
    paste0(first_position, " (", format(position_num, nsmall = 2), ") | ", advanced_position)
  })
  
  # ** Player's Age ----
  output$player_age <- renderUI({
    age = player_info_df()$age
    age_perc = round(100*player_info_df()$age_percentile_position, 0)
    HTML(paste0("Age: ", age, "<text style='font-size: 15px; ",
           "color:", get_percentile_color(age_perc), "'> ",
           age_perc, "</text>"))
  })
  
  # ** Player's Measurements ----
  output$player_measurement <- renderUI({
    height = player_info_df()$height
    height_perc = round(100*player_info_df()$height_percentile_position, 0)
    weight = player_info_df()$weight
    weight_perc = round(100*player_info_df()$weight_percentile_position, 0)
    HTML(
      paste0("Height: ", height, "<text style='font-size: 15px; ",
             "color:", get_percentile_color(height_perc), "'> ",
             height_perc, "</text> | Weight: ", weight, 
             "lbs<text style='font-size: 15px; ",
             "color:", get_percentile_color(weight_perc), "'> ",
             weight_perc, "</text>"   
          )
    )
    
    
  })
  
  # ** Salary ----
  output$player_salary <- renderTable({
    player_salary()
  },
  striped = TRUE,
  bordered = TRUE,
  width = '90%',
  align = 'c',
  sanitize.text.function = function(x) x)
  
  # ** Plot ----
  output$player_projection <- renderPlot({
    plot_player_projection(player_projection_df())
  })
  # ** Stats ----  
  output$player_table <- renderTable({
    player_stats()
  },
  striped = TRUE,
  bordered = TRUE,
  width = '100%',
  align = 'c',
  sanitize.text.function = function(x) x)
  
})
