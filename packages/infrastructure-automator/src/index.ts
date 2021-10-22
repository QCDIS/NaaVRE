import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { MainAreaWidget } from '@jupyterlab/apputils';

import { ILauncher } from '@jupyterlab/launcher';

import { buildIcon } from '@jupyterlab/ui-components';

import { InfrastructureAutomatorWidget } from './InfrastructureAutomator';

namespace CommandIDs {
    export const create = 'create-vre-infrastructure-automator';
}

const extension: JupyterFrontEndPlugin<void> = {
    id: 'vre-infrastructure-automator',
    autoStart: true,
    optional: [ILauncher],
    activate: (app: JupyterFrontEnd, launcher: ILauncher) => {
        const { commands } = app;
        const command = CommandIDs.create;
        commands.addCommand(command, {
            caption: 'Launch Infrastructure Automator',
            label: 'Infrastructure Automator',
            icon: args => (args['isPalette'] ? null : buildIcon),
            execute: () => {
              const content = new InfrastructureAutomatorWidget();
              const widget = new MainAreaWidget<InfrastructureAutomatorWidget>({ content });
              widget.title.label = 'Infrastructure Automator';
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