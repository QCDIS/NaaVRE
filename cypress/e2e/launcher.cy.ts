describe('Experiment Manager', () => {
  beforeEach(() => {
    cy.resetJupyterLab();
  });

  it('should have Experiment Manager extensions', () => {
    // cy.get('.jp-ToolbarButtonComponent[title="New Launcher"]').click({
    //   force: true
    // });
    // Jupyter notebook default kernel is available
    cy.get(
      '.jp-LauncherCard[data-category="Notebook"][title*="Python 3"]:visible'
    );
  });
});
