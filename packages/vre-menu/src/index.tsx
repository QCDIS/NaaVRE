import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IMainMenu } from '@jupyterlab/mainmenu';
import { Menu } from '@lumino/widgets';
import { ICommandPalette } from '@jupyterlab/apputils';
import { CounterWidget } from './widget';
import { MainAreaWidget } from '@jupyterlab/apputils';


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
        const commandSettings = 'naavre:settings';

        commands.addCommand(commandSettings, {
            label: 'Settings',
            caption: 'Settings',
            execute: (args: any) => {
                
                // TODO: Open dedicated settings page
            }
        });


        const commandExperimentManager = 'naavre:experiment-manager';

        commands.addCommand(commandExperimentManager, {
            label: 'CounterWidget',
            caption: 'CounterWidget',
            execute: (args: any) => {
                const content = new CounterWidget();
                const widget = new MainAreaWidget<CounterWidget>({ content });
                widget.title.label = 'CounterWidget';
                app.shell.add(widget, 'main');
            }
        });




        const category = 'NaaVRE';

        palette.addItem({
            command: commandSettings,
            category,
            args: { origin: 'from the palette' }
        });

        palette.addItem({
            command: commandExperimentManager,
            category,
            args: { origin: 'from the palette' }
        });

        // Create a menu
        const vreMenu: Menu = new Menu({ commands });
        vreMenu.title.label = 'NaaVRE'
        mainMenu.addMenu(vreMenu, { rank: 80 });
        vreMenu.addItem({ command: commandSettings, args: { origin: 'from the menu' } });
        vreMenu.addItem({ command: commandExperimentManager, args: { origin: 'from the menu' } });

    }
};

export default extension;