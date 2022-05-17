import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';

import * as React from 'react';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { Menu } from '@lumino/widgets';
import { ReactWidget, ICommandPalette, Dialog, showDialog } from '@jupyterlab/apputils';
import { CredentialsDialog } from './CredentialsDialog';

const extension: JupyterFrontEndPlugin<void> = {
    id: 'main-menu',
    autoStart: true,
    requires: [ICommandPalette, IMainMenu],
    activate: (
        app: JupyterFrontEnd,
        palette: ICommandPalette,
        mainMenu: IMainMenu
    ) => {

        const CredentialsDialogOptions: Partial<Dialog.IOptions<any>> = {
            title: '',
            body: ReactWidget.create(
                <CredentialsDialog />
            ) as Dialog.IBodyWidget<any>,
            buttons: []
        };

        const { commands } = app;
        const manageCredentialsCommand = 'naavre:manage-credentials';

        commands.addCommand(manageCredentialsCommand, {
            label: 'Manage Credentials',
            caption: 'Manage Credentials',
            execute: (args: any) => {
                showDialog(CredentialsDialogOptions);
            }
        });

        const category = 'NaaVRE';

        palette.addItem({
            command: manageCredentialsCommand,
            category,
            args: { origin: 'from the palette' }
        });

        // Create a menu
        const vreMenu: Menu = new Menu({ commands });
        vreMenu.title.label = 'NaaVRE'
        mainMenu.addMenu(vreMenu, { rank: 80 });
        vreMenu.addItem({ command: manageCredentialsCommand, args: { origin: 'from the menu' } });

    }
};

export default extension;