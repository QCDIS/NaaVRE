import {CommandRegistry} from '@lumino/commands'
import {IFileBrowserFactory} from "@jupyterlab/filebrowser";
import {LabIcon} from "@jupyterlab/ui-components";

import {WorkflowWidget} from "./widget";

const wfIcon = new LabIcon({
  name: 'launcher:python-icon',
  svgstr: '<svg xmlns="http://www.w3.org/2000/svg" width="66.69" height="66.69" viewBox="0 0 66.69 66.69"><defs><style>      .a92fba6e-7ebd-4c32-8963-8296e20ef654 {        fill: #0f4e8b;      }    </style></defs><g id="a472ef7c-dd17-4d49-9df0-027f7f177a8f" data-name="Livello 2"><g id="b55479a9-ce75-42ce-9f6a-fdbd00d931c6" data-name="Livello 1"><g><path class="a92fba6e-7ebd-4c32-8963-8296e20ef654" d="M33.34,40.87a5.38,5.38,0,1,0,5.38,5.38,5.39,5.39,0,0,0-5.38-5.38Zm0,8.61a3.23,3.23,0,1,1,3.23-3.23,3.23,3.23,0,0,1-3.23,3.23Z"></path><rect class="a92fba6e-7ebd-4c32-8963-8296e20ef654" x="32.27" y="4.3" width="8.6" height="2.15"></rect><rect class="a92fba6e-7ebd-4c32-8963-8296e20ef654" x="32.27" y="8.6" width="8.6" height="2.15"></rect><rect class="a92fba6e-7ebd-4c32-8963-8296e20ef654" x="25.81" y="12.91" width="15.06" height="2.15"></rect><rect class="a92fba6e-7ebd-4c32-8963-8296e20ef654" x="25.81" y="17.21" width="15.06" height="2.15"></rect><rect class="a92fba6e-7ebd-4c32-8963-8296e20ef654" x="25.81" y="21.51" width="15.06" height="2.15"></rect><path class="a92fba6e-7ebd-4c32-8963-8296e20ef654" d="M66.69,34.42V25.81H51.63v8.61h6.45V45.17H45.17V43.32l-2.64-.88L43.78,40l-4.14-4.14-2.49,1.25-.88-2.64H34.42V28H45.17V15.06H58.08v6L55.62,18.6l-1.53,1.52,5.07,5.06,5.06-5.06L62.7,18.6l-2.47,2.47V12.91H45.17V0H28.6L21.51,7.08v5.83H6.45v8.16L4,18.6,2.47,20.12l5.06,5.06,5.06-5.06L11.07,18.6,8.6,21.07v-6H21.51V28H32.27v6.45H30.42l-.88,2.64-2.49-1.25L22.91,40l1.24,2.49-2.64.88v1.85H8.6V34.42h6.46V25.81H0v8.61H6.45V51.78a4.31,4.31,0,1,0,2.15,0V47.33h6.46v13.1a3.23,3.23,0,1,0,2.15,0V47.33h4.3v1.85l2.64.88-1.24,2.49,4.14,4.14,2.49-1.25.88,2.64h5.85l.88-2.64,2.49,1.25,4.14-4.14-1.25-2.49,2.64-.88V47.33h4.31v13.1a3.23,3.23,0,1,0,2.15,0V47.33h6.45v4.45a4.31,4.31,0,1,0,2.15,0V34.42ZM28,3.67V6.45H25.18ZM23.66,8.6h6.46V2.15H43V25.81H23.66ZM2.15,28H12.91v4.3H2.15Zm7.53,28a2.15,2.15,0,1,1-2.15-2.15,2.15,2.15,0,0,1,2.15,2.15Zm6.45,8.61a1.08,1.08,0,1,1,1.08-1.08,1.08,1.08,0,0,1-1.08,1.08ZM43,47.63l-2.46.82-.19.47c0,.14-.1.28-.16.41L40,49.8l1.16,2.32-1.94,2-2.33-1.16-.46.2-.41.17-.48.18-.82,2.47H32l-.83-2.47-.48-.18-.4-.17-.46-.2-2.33,1.16-1.95-2,1.17-2.32-.21-.47c-.06-.13-.11-.27-.17-.41l-.18-.47-2.47-.82V44.87l2.47-.82.18-.47c.06-.14.11-.28.17-.41l.21-.47-1.17-2.32,1.95-2,2.33,1.16.46-.2.4-.17.48-.18L32,36.57h2.75L35.54,39l.48.18.41.17.46.21,2.33-1.17,1.94,2L40,42.7l.21.47c.06.13.11.27.17.41l.18.47,2.46.83Zm7.53,16.91a1.08,1.08,0,1,1,1.08-1.08,1.08,1.08,0,0,1-1.08,1.08Zm10.76-8.61a2.15,2.15,0,1,1-2.15-2.15,2.15,2.15,0,0,1,2.15,2.15ZM53.78,28H64.54v4.3H53.78Z"></path></g></g></g></svg>',
});

export namespace CommandIDs {
  export const createNew = 'create-vre-composer'
}

export namespace Commands {

  async function createNew(
    commands: CommandRegistry,
    cwd: string,
    FACTORY: string,
  ) {
    const model = await commands.execute('docmanager:new-untitled', {
      path: cwd,
      type: 'file',
      ext: 'naavrewf',
    });
    if (model != undefined) {
      const widget = ((await commands.execute('docmanager:open', {
        path: model.path,
        factory: FACTORY
      })) as unknown) as WorkflowWidget;
      widget.isUntitled = true;
      return widget;
    }
  }

  export function addCommands(
    commands: CommandRegistry,
    browserFactory: IFileBrowserFactory,
    FACTORY: string,
  ) {

    commands.addCommand(CommandIDs.createNew, {
      label: 'Experiment Manager',
      caption: 'Launch Workflow Composition',
      icon: args => (args['isPalette'] ? null : wfIcon),
      execute: args => {
        return createNew(
          commands,
          (args.cwd || browserFactory.defaultBrowser.model.path) as string,
          FACTORY,
        );
      }
    });

  }

}
