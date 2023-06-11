describe('JupyterLab', () => {
  beforeEach(() => {
    // Visit the JupyterLab URL or start from a specific page if needed
    cy.visit('')
    cy.wait(5000) // Adjust the timeout as needed
  })



  it('should open a notebook and execute code', () => {
    // Open a notebook file
    cy.contains('.jp-DirListing-item[title="test_notebook.ipynb"]').click();
//
//     // Wait for the notebook to load
//     cy.get('.jp-mod-notebookPanel').should('be.visible')
//
//     // Get the first code cell in the notebook
//     cy.get('.jp-NotebookPanel-notebook .jp-Cell').first().as('codeCell')
//
//     // Execute the code cell
//     cy.get('@codeCell')
//       .click()
//       .type('{enter}')
//
//     // Wait for the execution to complete
//     cy.get('@codeCell').should('have.class', 'jp-mod-executing')
//     cy.get('@codeCell').should('not.have.class', 'jp-mod-executing')
//
//     // Check for the output of the executed code
//     cy.get('@codeCell').next('.jp-OutputArea').should('be.visible')
  })

  it('should create a new Python notebook', () => {
    // Click on the "New" button
    cy.get('.jp-ToolbarButtonComponent[data-category="Notebook"]').click()

    // Select "Python 3" from the dropdown menu
    cy.get('.jp-MenuBar-menu .jp-MenuBar-item')
      .contains('Python 3')
      .click()

    // Wait for the new notebook to be created
    cy.get('.jp-mod-notebookPanel').should('be.visible')
  })
})