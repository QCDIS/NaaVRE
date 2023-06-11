describe('JupyterLab', () => {
  beforeEach(() => {
    // Visit the JupyterLab URL or start from a specific page if needed
    cy.visit('?reset')
    cy.wait(15000) // Adjust the timeout as needed
  })



//   it('should open a notebook and execute code', () => {
//     // Open a notebook file
//     cy.contains('.jp-DirListing-item', 'test_notebook.ipynb').click()
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
//   })

  it('should create a new Python notebook', () => {
  cy.get(
    `.jp-LauncherCard[data-category="Notebook"][title="Python 3 (ipykernel)"]:visible`
  ).click();

  // Get the code cell you want to add content to
  cy.get('.jp-NotebookPanel-notebook .jp-Cell').first().as('codeCell1');

  // Click on the code cell to activate it
  cy.get('@codeCell1').click();

  // Type or paste content into the code cell
  cy.get('@codeCell1').type('print("Hello, World!")');

  // Verify that the content is added to the code cell
  cy.get('@codeCell1').contains('print("Hello, World!")').should('be.visible');




  });
})
