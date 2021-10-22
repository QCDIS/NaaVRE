import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { MainAreaWidget } from '@jupyterlab/apputils';

import { ILauncher } from '@jupyterlab/launcher';

import { runIcon } from '@jupyterlab/ui-components';

import { WorkflowsWidget } from './Workflows';

namespace CommandIDs {
    export const create = 'create-vre-workflows';
}

const extension: JupyterFrontEndPlugin<void> = {
    id: 'vre-workflows',
    autoStart: true,
    optional: [ILauncher],
    activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
        const { commands } = app;
        const command = CommandIDs.create;
        commands.addCommand(command, {
            caption: 'Launch workflows management',
            label: 'Workflows',
            icon: args => (args['isPalette'] ? null : runIcon),
            execute: () => {
              const content = new WorkflowsWidget();
              const widget = new MainAreaWidget<WorkflowsWidget>({ content });
              widget.title.label = 'Workflows';
              widget.title.icon = runIcon;
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