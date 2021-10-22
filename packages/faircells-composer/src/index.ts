import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { MainAreaWidget } from '@jupyterlab/apputils';

import { ILauncher } from '@jupyterlab/launcher';

import { buildIcon } from '@jupyterlab/ui-components';

import { ComposerWidget } from './Composer';

namespace CommandIDs {
    export const create = 'create-vre-composer';
}

const extension: JupyterFrontEndPlugin<void> = {
    id: 'vre-composer',
    autoStart: true,
    optional: [ILauncher],
    activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
        const { commands } = app;
        const command = CommandIDs.create;
        commands.addCommand(command, {
            caption: 'Launch Workflow Composition',
            label: 'Experiment Manager',
            icon: args => (args['isPalette'] ? null : buildIcon),
            execute: () => {
              const content = new ComposerWidget();
              const widget = new MainAreaWidget<ComposerWidget>({ content });
              widget.title.label = 'Experiment Manager';
              widget.title.icon = buildIcon;
              app.shell.add(widget, 'main');
            }
        });
      
        if (launcher) {
            launcher.add({
                command,
                category: 'LifeWatch VRE'        
            }); 
        }
    }
};

export default extension;