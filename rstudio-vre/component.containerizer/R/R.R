#' @import shiny
#' @import rstudioapi
#' @import parsermd

main <- function() {
  ui <- fluidPage(
    h1('Cell Containerizer'),
    htmlOutput('doc_info_output'),
    actionButton('parse_button', 'Parse'),
    selectInput('code_chunk_selector', 'Select Code Chunk', c(), selectize=TRUE),
    htmlOutput('code_output'),

    selectInput('base_image_selector', 'Base Image', c()),
    actionButton('create_button', 'Create'),
  )
  server <- function(input, output, session) {
    linesep <- '\n'

    API_ENDPOINT <- Sys.getenv('API_ENDPOINT')
    CONTAINERIZER_PREFIX <- 'api/containerizer'
    NAAVRE_API_TOKEN <- Sys.getenv('NAAVRE_API_TOKEN')
    choices_placeholder = c(' ') # # blank [ex. c(), c(''), list(), list('')] or NULL will not trigger event handler thus code_output will not be updated. https://bookdown.org/yihui/rmarkdown/r-code.html does not recommend using spaces in code chunk labels.

    current_doc <- NULL
    results <- NULL
    selected_code <- ''

    parse_md <- function() {
      current_doc <<- rstudioapi::getSourceEditorContext()
      error <- ''
      rmd <- NULL
      rmd_chunks <- list() # c() causes 'Error in <-: attempt to set an attribute on NULL'
      rmd_chunk_indices <- list()
      rmd_offset_indices <- list()
      tryCatch({
        rmd <- parsermd::parse_rmd(current_doc$content)
        for (i in seq_along(rmd)) {
          node <- rmd[[i]]
          node_type <- parsermd::rmd_node_type(node)
          if (node_type == 'rmd_chunk') {
            p <- length(rmd_chunks) + 1
            rmd_chunks[[p]] <- node
            rmd_chunk_indices[[p]] <- i
          }
          else if (node_type == 'rmd_heading' && i < length(rmd) && parsermd::rmd_node_type(rmd[[i + 1]]) == 'rmd_markdown') {
            p <- length(rmd_offset_indices) + 1
            rmd_offset_indices[[p]] <- i
          }
        }
        if (length(rmd_chunks) == 0) {
          selected_code <<- ''
          updateSelectInput(session, 'code_chunk_selector', choices=choices_placeholder)
          error <- 'no code' # don't use operator<<- here, or this will be '' (blank)
        }
      }, error = function(e) {
        selected_code <<- ''
        updateSelectInput(session, 'code_chunk_selector', choices=choices_placeholder)
        error <<- 'parsing'
      })
      return(list('error'=error, 'rmd'=rmd, 'rmd_chunks'=rmd_chunks, 'rmd_chunk_indices'=rmd_chunk_indices, 'rmd_offset_indices'=rmd_offset_indices))
    }

    observeEvent(input$parse_button, {
      results <<- parse_md()
      output$doc_info_output <- renderUI({
        HTML(paste0(
          '<b>Document ID: </b>', current_doc$id, '<br>',
          '<b>Document Path: </b>', current_doc$path, '<br>',
          switch(results[['error']],
                 'no code'='No code snippets found',
                 'parsing'='<p style="color:red;">Parsing ERROR</p>',
                 'Parsing done')
        )) # cat/paste0 cannot handle trailing comma in its arg list
      })
      if (results[['error']] != '') { rmd_chunk_labels <<- list() } # c() returns NULL
      else { rmd_chunk_labels <- lapply(results[['rmd_chunks']], function(node) parsermd::rmd_node_label(node)) }
      updateSelectInput(session, 'code_chunk_selector', choices=setNames(results[['rmd_chunk_indices']], rmd_chunk_labels))
    })

    observeEvent(input$code_chunk_selector, {
      cell_index <- as.numeric(input$code_chunk_selector)

      output$code_output <- renderUI({
        if (is.na(cell_index)) { selected_code <<- '' }
        else {
          selected_node <- results$rmd[[cell_index]]
          if (is.null(selected_node)) { selected_code <<- '' }
          else {
            code_statements <- parsermd::rmd_node_code(selected_node)
            selected_code <<- paste(unlist(code_statements), collapse='<br>')
          }
        }
        return(HTML(paste0('<pre>', selected_code, '</pre>')))
      })

      if (!is.na(cell_index)) {
        request <- httr2::request(stringr::str_interp('${API_ENDPOINT}/${CONTAINERIZER_PREFIX}/extract'))
        request <- httr2::req_method(request, 'POST')
        request <- httr2::req_headers(request, Authorization=stringr::str_interp('Token ${NAAVRE_API_TOKEN}'), 'Content-Type'='application/json')
        request <- httr2::req_body_raw(request, jsonlite::toJSON(
          list(
            'rmarkdown' = paste0(current_doc$content, collapse='\n'),
            'rmarkdown_offset_indices' = results$rmd_offset_indices,
            'cell_index' = cell_index,
            'kernel' = switch(parsermd::rmd_node_engine(results$rmd[[cell_index]]), 'r'='IRkernel', 'python'='ipykernel', '')
          ),
          auto_unbox = TRUE)
        )
        tryCatch({
          response <- httr2::req_perform(request)
          print(jsonlite::prettify(httr2::resp_body_json(response)))
        }, error=function(e) { print(e) })
      }
    })

    parse_md()

    request <- httr2::request(stringr::str_interp('${API_ENDPOINT}/${CONTAINERIZER_PREFIX}/baseimagetags'))
    request <- httr2::req_headers(request, Authorization=stringr::str_interp('Token ${NAAVRE_API_TOKEN}'))
    tryCatch({
      response <- httr2::req_perform(request)
      base_image_list <- httr2::resp_body_json(response)
      updateSelectInput(session, 'base_image_selector', choices=names(base_image_list), selected='r')
    }, error=function(e) { print(e) })
  }
  runGadget(ui, server)
}
