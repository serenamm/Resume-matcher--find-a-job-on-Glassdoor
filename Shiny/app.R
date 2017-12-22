library(shiny)
library(shinydashboard)
library(dplyr)
library(tidyr)
library(DT)
library(PythonInR)
library(pdftools)

working_directory = "C:/Data/Projects/Glassdoor"
setwd(working_directory)
pyConnect()
pyExecfile("helper.py")

ui = 
  dashboardPage(
    dashboardHeader(title = 'Dashboard'),
    dashboardSidebar(
      sidebarMenu(
        menuItem("About", tabName = "about", icon = icon("info")),
        menuItem("Search Job", tabName = "search", icon = icon("database")),
        fileInput('file1', "Insert your CV as PDF file",
                  accept=c('pdf'))
        
      )
    ),
    dashboardBody(
      tabItems(
        tabItem(tabName = 'about',
                fluidRow(
                  box(title = 'Resume Text Analysis and Job Matching', status = "primary", solidHeader = TRUE, collapsible = F, width = 12,
                      br(),
                      tags$p("This app allows a user to upload their resume and return their best job matches on Glassdoor.ca, based on cosine similarity.")
                      ))
                #,
                # fluidRow(
                #   box(title = "About Me", status = "primary", solidHeader = TRUE, collapsible = T, collapsed = T,width = 12,
                #       column(
                #         width = 10,
                #         h4("Serena McDonnell"),
                #         tags$p("I'm Serena!"),
                #         
                #         tags$hr()
                #         )
                #       ))
                ),
        tabItem(tabName = "search",
                fluidRow(
                  box(width = NULL, status = "primary", solidHeader = TRUE,
                      title = "Your top matches on Glassdoor!",dataTableOutput("table"))
                )
        )
                  )
        )
    )

server = function(input, output){
  output$table <- renderDataTable({
    inFile <- input$file1
    if (is.null(inFile))
      return(NULL)
    
    cvPdf = paste(pdf_text(inFile$datapath),collapse = '')
    pyCall('get_best_csv', cvPdf)
    f = read.csv('best_match_df.csv',
                 sep = ",",dec = ".", stringsAsFactors = F) 
    data = f%>% mutate(.,Link = sprintf('<a href="%s" target="_blank" class="btn btn-primary">Info</a>',Link))
    return(data[,-1])
  }, escape = FALSE )
}

shinyApp(ui, server)