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

  // Create a new code cell
  cy.get('.jp-NotebookPanel-toolbar .jp-ToolbarButtonComponent[title="Insert a cell below (B)"]').click();

  // Get the new code cell you want to add content to
  cy.get('.jp-NotebookPanel-notebook .jp-Cell').eq(1).as('codeCell2');

  // Execute cell 1 by pressing shift+enter
  cy.get('@codeCell1').type('{shift}{enter}');


  // Click on the code cell to activate it
    cy.get('@codeCell2').click();

  // Type or paste content into the code cell
  cy.get('@codeCell2').type('print("Hello, Universe!")');

  cy.get('@codeCell2').contains('print("Hello, Universe!")').should('be.visible');

  // Execute cell 2 by pressing shift+enter
  cy.get('@codeCell2').type('{shift}{enter}');

  //Save the notebook
  cy.get('.jp-NotebookPanel-toolbar .jp-ToolbarButtonComponent[title="Save and create checkpoint (Ctrl+S)"]').click();

  //In the pop-up window, click on the "Rename" button
  cy.get('.jp-Dialog-content .jp-Dialog-button.jp-mod-accept').click();

  //click on the element with the title "Notebook Search"
  cy.get('.lm-TabBar-tab.p-TabBar-tab[title="Notebook Search"]').click();

  //click on the element with the title "LifeWatch Panel"
  cy.get('.lm-TabBar-tab.p-TabBar-tab[title="LifeWatch Panel"]').click();


  });
})




