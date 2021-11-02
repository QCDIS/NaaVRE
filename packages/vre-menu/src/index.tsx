import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';

import * as React from 'react';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { requestAPI } from '@jupyter_vre/core';
import { Menu } from '@lumino/widgets';
import { ICommandPalette, showDialog, Dialog } from '@jupyterlab/apputils';
import { AuthDialog } from './AuthDialog';
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
    const auth_remote_storage_command = 'vre:cred:remote-storage-auth';
    const auth_registry_command = 'vre:cred:container-registry-auth';

    const SDIACredDialogOptions: Partial<Dialog.IOptions<any>> = {
        title: 'Infrastructure Automator Credentials',
        body: formDialogWidget(
          <AuthDialog />
        ),
        buttons: [Dialog.cancelButton(), Dialog.okButton({ label: 'Save' })],
        defaultButton: 1
    };

    commands.addCommand(auth_sdia_command, {
        label: 'SDIA',
        caption: 'SDIA',
        execute: (args: any) => {
            showDialog(SDIACredDialogOptions).then((res) => {

                requestAPI<any>('sdia/testauth', {
                    body: JSON.stringify(res.value),
                    method: 'POST'
                }).then((resp) => {
                    console.log(resp);
                });
        });
        }
    });

    // commands.addCommand(auth_remote_storage_command, {
    //     label: 'Remote Storage',
    //     caption: 'Remote Storage',
    //     execute: (args: any) => {
    //         showDialog({
    //             title: 'Remote Storage Credentials',
    //             body: (
    //               <AuthDialog />
    //             ),
    //             buttons: [Dialog.okButton()]
    //         }).then((res) => {
                
    //         });
    //     }
    // });

    // commands.addCommand(auth_registry_command, {
    //     label: 'Container Registry',
    //     caption: 'Container Registry',
    //     execute: (args: any) => {
    //         showDialog({
    //             title: 'Container Registry Credentials',
    //             body: (
    //               <AuthDialog />
    //             ),
    //             buttons: [Dialog.okButton()]
    //         }).then((res) => {
                
    //         });
    //     }
    // });

    const category = 'LifeWatch VRE';
        palette.addItem({
        command: auth_sdia_command,
        category,
        args: { origin: 'from the palette' }
    });

    // Create a menu
    const vreMenu: Menu = new Menu({ commands });
    vreMenu.title.label = 'LifeWatch VRE';

    const credentialsMenu: Menu = new Menu({ commands });
    credentialsMenu.title.label = 'Manage Credentials'
    credentialsMenu.addItem({ command: auth_sdia_command, args: { origin: 'from the menu' }});
    credentialsMenu.addItem({ command: auth_remote_storage_command, args: { origin: 'from the menu' }});
    credentialsMenu.addItem({ command: auth_registry_command, args: { origin: 'from the menu' }});
    
    vreMenu.addItem({ submenu: credentialsMenu, type: 'submenu' });
    mainMenu.addMenu(vreMenu, { rank: 100 });
}
};

export default extension;