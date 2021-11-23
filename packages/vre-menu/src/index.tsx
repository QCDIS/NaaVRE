import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';

import * as React from 'react';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { requestAPI } from '@jupyter_vre/core';
import { Menu } from '@lumino/widgets';
import { ICommandPalette, showDialog, Dialog } from '@jupyterlab/apputils';
import { SDIAAuthDialog } from './SDIAAuthDialog';
import { GithubAuthDialog } from './GithubAuthDialog';
import { formDialogWidget } from './formDialogWidget';
  
/**
 * Initialization data for the main menu example.
 */
const extension: JupyterFrontEndPlugin<void> = {
id: 'main-menu',
autoStart: true,
requires: [ICommandPalette, IMainMenu],
activate: (
    app: JupyterFrontEnd,
    palette: ICommandPalette,
    mainMenu: IMainMenu
) => {

    const { commands } = app;
    const auth_sdia_command = 'vre:cred:sdia-auth';
    const auth_github_command = 'vre:cred:github-auth';

    const SDIACredDialogOptions: Partial<Dialog.IOptions<any>> = {
        title: 'Infrastructure Automator Credentials',
        body: formDialogWidget(
          <SDIAAuthDialog />
        ),
        buttons: [Dialog.cancelButton(), Dialog.okButton({ label: 'Save' })],
        defaultButton: 1
    };

    const GithubDialogOptions: Partial<Dialog.IOptions<any>> = {
        title: 'Github Token',
        body: formDialogWidget(
          <GithubAuthDialog />
        ),
        buttons: [Dialog.cancelButton(), Dialog.okButton({ label: 'Save' })],
        defaultButton: 1
    };

    commands.addCommand(auth_sdia_command, {
        label: 'SDIA',
        caption: 'SDIA',
        execute: (args: any) => {
            showDialog(SDIACredDialogOptions).then((res: { value: any; }) => {

                requestAPI<any>('sdia/testauth', {
                    body: JSON.stringify(res.value),
                    method: 'POST'
                }).then((resp: any) => {
                    console.log(resp);
                });
            });
        }
    });

    commands.addCommand(auth_github_command, {
        label: 'Github',
        caption: 'Github',
        execute: (args: any) => {
            showDialog(GithubDialogOptions).then((res: { value: any; }) => {

                requestAPI<any>('github/savetoken', {
                    body: JSON.stringify(res.value),
                    method: 'POST'
                }).then((resp: any) => {
                    console.log(resp);
                });
            });
        }
    });

    const category = 'LifeWatch VRE';

    palette.addItem({
        command: auth_sdia_command,
        category,
        args: { origin: 'from the palette' }
    });

    palette.addItem({
        command: auth_github_command,
        category,
        args: { origin: 'from the palette' }
    });

    // Create a menu
    const vreMenu: Menu = new Menu({ commands });
    vreMenu.title.label = 'LifeWatch VRE';

    const credentialsMenu: Menu = new Menu({ commands });
    credentialsMenu.title.label = 'Manage Credentials'
    credentialsMenu.addItem({ command: auth_sdia_command, args: { origin: 'from the menu' }});
    credentialsMenu.addItem({ command: auth_github_command, args: { origin: 'from the menu' }});
    
    vreMenu.addItem({ submenu: credentialsMenu, type: 'submenu' });
    mainMenu.addMenu(vreMenu, { rank: 100 });
}
};

export default extension;