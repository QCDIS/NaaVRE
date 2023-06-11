/// <reference types="cypress" />
// ***********************************************
// This example commands.ts shows you how to
// create various custom commands and overwrite
// existing commands.
//
// For more comprehensive examples of custom
// commands please read more here:
// https://on.cypress.io/custom-commands
// ***********************************************
//
//
// -- This is a parent command --
// Cypress.Commands.add('login', (email, password) => { ... })
//
//
// -- This is a child command --
// Cypress.Commands.add('drag', { prevSubject: 'element'}, (subject, options) => { ... })
//
//
// -- This is a dual command --
// Cypress.Commands.add('dismiss', { prevSubject: 'optional'}, (subject, options) => { ... })
//
//
// -- This will overwrite an existing command --
// Cypress.Commands.overwrite('visit', (originalFn, url, options) => { ... })
//
// declare global {
//   namespace Cypress {
//     interface Chainable {
//       login(email: string, password: string): Chainable<void>
//       drag(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       dismiss(subject: string, options?: Partial<TypeOptions>): Chainable<Element>
//       visit(originalFn: CommandOriginalFn, url: string, options: Partial<VisitOptions>): Chainable<Element>
//     }
//   }
// }





Cypress.Commands.add('deleteFile', (name: string): void => {
  cy.exec(`find build/cypress-tests/ -name "${name}" -delete`, {
    failOnNonZeroExit: false
  });
});


Cypress.Commands.add('openFile', (name: string): void => {
  cy.findByRole('listitem', {
    name: (n, _el) => n.includes(name),
    timeout: 50000
  }).dblclick();
});


Cypress.Commands.add(
  'openFileAndCheckContent',
  (fileExtension: string): void => {
    cy.openHelloWorld(fileExtension);
    // Ensure that the file contents are as expected
    cy.get('span[role="presentation"]').should($span => {
      expect($span.get(0).innerText).to.eq('print("Hello Elyra")');
    });

    // Close the file editor
    cy.closeTab(-1);
  }
);

Cypress.Commands.add('bootstrapFile', (name: string): void => {
  cy.readFile(`cypress/assets/${name}`).then((file: any) => {
    cy.writeFile(`build/cypress-tests/${name}`, file);
  });
});