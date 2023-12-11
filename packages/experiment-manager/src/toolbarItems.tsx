import {CommandRegistry} from '@lumino/commands'
import {Widget} from '@lumino/widgets';
import {
  ToolbarButton,
  showDialog,
} from '@jupyterlab/apputils';
import {
  addIcon,
  codeIcon,
  fileIcon,
  runIcon,
  saveIcon,
} from '@jupyterlab/ui-components'

import {WorkflowWidget} from "./widget";

export namespace ToolbarItems {

  export function createCellsCatalogButton(widget: WorkflowWidget): Widget {
    return new ToolbarButton({
      label: 'Cells catalog',
      tooltip: 'Open the cells catalog',
      icon: addIcon,
      onClick: () => {showDialog(widget.content.composerRef.current.CatalogDialogOptions)},
    })
  }

  export function createLoadButton(widget: WorkflowWidget): Widget {
    return new ToolbarButton({
      label: 'Load',
      tooltip: 'Load a workflow',
      icon: fileIcon,
      onClick: () => {widget.content.composerRef.current.loadWorkflow()},
    })
  }

  export function createSaveButton(widget: WorkflowWidget, commands: CommandRegistry): Widget {
    return new ToolbarButton({
      label: 'Save',
      tooltip: 'Save the workflow',
      icon: saveIcon,
      onClick: () => {commands.execute('docmanager:save')},
    })
  }

  export function createExportButton(widget: WorkflowWidget): Widget {
    return new ToolbarButton({
      label: 'Export',
      tooltip: 'Export the workflow',
      icon: codeIcon,
      onClick: () => {widget.content.composerRef.current.exportWorkflow()},
    })
  }

  export function createRunButton(widget: WorkflowWidget): Widget {
    return new ToolbarButton({
      label: 'Run',
      tooltip: 'Run the workflow',
      icon: runIcon,
      onClick: () => showDialog(widget.content.composerRef.current.ExecuteWorkflowDialogOptions),
    })
  }

}
