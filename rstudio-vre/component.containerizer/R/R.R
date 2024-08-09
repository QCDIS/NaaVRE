#' @import shiny
#' @import shinyjs
#' @import rjson
#' @import rstudioapi
#' @import parsermd

main <- function() {
  ui <- fluidPage(
    shinyjs::useShinyjs(),
    h1('Cell Containerizer'),
    htmlOutput('doc_info_output'),
    actionButton('parse_button', 'Parse'),
    selectInput('code_chunk_selector', 'Select Code Chunk', c(), selectize=TRUE),
    htmlOutput('code_output'),
    div(
      id='inputs_div',
      h4('Inputs')
    ),
    div(
      id='outputs_div',
      h4('Outputs')
    ),
    selectInput('base_image_selector', 'Base Image', c()),
    actionButton('create_button', 'Create'),
  )
  server <- function(input, output, session) {
    linesep <- '\n'
    type_choices = c('Integer'='int', 'Float'='float', 'String'='str', 'List'='list')

    API_ENDPOINT <- Sys.getenv('API_ENDPOINT')
    CONTAINERIZER_PREFIX <- 'api/containerizer'
    NAAVRE_API_TOKEN <- Sys.getenv('NAAVRE_API_TOKEN')
    choices_placeholder <- c(' ') # # blank [ex. c(), c(''), list(), list('')] or NULL will not trigger event handler thus code_output will not be updated. https://bookdown.org/yihui/rmarkdown/r-code.html does not recommend using spaces in code chunk labels.

    base_image_list <- list()
    current_doc <- NULL
    parsing_results <- NULL
    selected_code <- ''
    extraction_results <- list()

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
          else if (
            (node_type == 'rmd_heading' && i < length(rmd) && parsermd::rmd_node_type(rmd[[i + 1]]) == 'rmd_markdown')
            || (node_type == 'rmd_yaml_list' && parsermd::rmd_node_length(node) == 0)
          ) {
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
      parsing_results <<- parse_md()
      output$doc_info_output <- renderUI({
        HTML(paste0(
          '<b>Document ID: </b>', current_doc$id, '<br>',
          '<b>Document Path: </b>', current_doc$path, '<br>',
          switch(parsing_results[['error']],
                 'no code'='No code snippets found',
                 'parsing'='<p style="color:red;">Parsing ERROR</p>',
                 'Parsing done')
        )) # cat/paste0 cannot handle trailing comma in its arg list
      })
      if (parsing_results[['error']] != '') { rmd_chunk_labels <<- list() } # c() returns NULL
      else { rmd_chunk_labels <- lapply(parsing_results[['rmd_chunks']], function(node) parsermd::rmd_node_label(node)) }
      updateSelectInput(session, 'code_chunk_selector', choices=setNames(parsing_results[['rmd_chunk_indices']], rmd_chunk_labels))
    })

    observeEvent(input$code_chunk_selector, {
      cell_index <- as.numeric(input$code_chunk_selector)

      output$code_output <- renderUI({
        if (is.na(cell_index)) { selected_code <<- '' }
        else {
          selected_node <- parsing_results$rmd[[cell_index]]
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
            'rmarkdown_offset_indices' = parsing_results$rmd_offset_indices,
            'cell_index' = cell_index,
            'kernel' = switch(parsermd::rmd_node_engine(parsing_results$rmd[[cell_index]]), 'r'='IRkernel', 'python'='ipykernel', '')
          ),
          auto_unbox = TRUE)
        )
        tryCatch({
          response <- httr2::req_perform(request)
          extraction_results <<- rjson::fromJSON(httr2::resp_body_json(response), simplify=FALSE)
        }, error=function(e) { print(e) })

        if ('inputs' %in% names(extraction_results) && length(extraction_results[['inputs']]) != 0) {
          inputs <- extraction_results[['inputs']]
          removeUI('div:has(> [id^="input_type_"])', multiple=TRUE)
          lapply(grep('^input_type_', names(input), value=TRUE), function(id) { removeUI(paste0('#', id)) })
          insertUI(selector='#inputs_div', where='beforeEnd',
                   ui=tagList(lapply(1:length(inputs), function(i) { selectInput(paste0('input_type_', inputs[i]), inputs[i], choices=type_choices) }))
          )
          shinyjs::show('inputs_div')
        }
        else { shinyjs::hide('inputs_div') }

        if ('outputs' %in% names(extraction_results) && length(extraction_results[['outputs']]) != 0) {
          outputs <- extraction_results[['outputs']]
          removeUI('div:has(> [id^="output_type_"])', multiple=TRUE)
          insertUI(selector='#outputs_div', where='beforeEnd',
                   ui=tagList(lapply(1:length(outputs), function(i) { selectInput(paste0('output_type_', outputs[i]), outputs[i], choices=type_choices) }))
          )
          shinyjs::show('outputs_div')
        }
        else { shinyjs::hide('outputs_div') }
      }
    })

    observeEvent(input$create_button, {
      extraction_results[['base_image']] <- base_image_list[[input$base_image_selector]]
      prefices <- c('input_type_', 'output_type_')
      for (prefix in prefices) {
        type_IDs <- grep(paste0('^', prefix), names(input), value=TRUE)
        if (length(type_IDs) > 0) {
          types <- list()
          for (ID in type_IDs) { types[[substr(ID, nchar(prefix) + 1, nchar(ID))]] <- input[[ID]] }
          extraction_results[['types']] <- types
          break
        }
      }

      request <- httr2::request(stringr::str_interp('${API_ENDPOINT}/${CONTAINERIZER_PREFIX}/addcell'))
      request <- httr2::req_method(request, 'POST')
      request <- httr2::req_headers(request, Authorization=stringr::str_interp('Token ${NAAVRE_API_TOKEN}'), 'Content-Type'='application/json')
      # print(rjson::toJSON(extraction_results))
      request <- httr2::req_body_raw(request, rjson::toJSON(extraction_results))
      tryCatch({
        response <- httr2::req_perform(request)
        print(httr2::resp_body_json(response))
      }, error=function(e) { print(e) })
    })

    shinyjs::hide('inputs_div')
    shinyjs::hide('outputs_div')

    parsing_results <- parse_md()

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
