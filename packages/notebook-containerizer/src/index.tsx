import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ToolbarButton, ReactWidget, Dialog, showDialog } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import {
    INotebookModel, INotebookTracker, NotebookPanel
} from '@jupyterlab/notebook';
import { DisposableDelegate, IDisposable } from '@lumino/disposable';
import * as React from 'react';
import { NotebookContainerizerDialog } from './NotebookContainerizerDialog';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
    activate,
    id: 'toolbar-containerize-notebook',
    autoStart: true,
    requires: [INotebookTracker]
};

export class NotebookSearchExtension implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {

    notebookTracker: INotebookTracker

    constructor(notebookTracker: INotebookTracker) {
        this.notebookTracker = notebookTracker;
    }

    createNew(
        panel: NotebookPanel,
        _context: DocumentRegistry.IContext<INotebookModel>
    ): IDisposable {

        const containerizeNotebook = () => {

            const catalogOptions: Partial<Dialog.IOptions<any>> = {
                title: '',
                body: ReactWidget.create(
                    <NotebookContainerizerDialog notebookTracker={this.notebookTracker}/>
                ) as Dialog.IBodyWidget<any>,
                buttons: []
            };
        

            showDialog(catalogOptions);
        };

        const button = new ToolbarButton({
            className: 'notebook-containerizer',
            label: 'Notebooks Containerizer',
            onClick: containerizeNotebook,
            tooltip: 'Notebooks Containerizer',
        });

        panel.toolbar.insertItem(10, 'containerizeNotebooks', button);
        return new DisposableDelegate(() => {
            button.dispose();
        });
    }
}

/**
 * Activate the extension.
 *
 * @param app Main application object
 */
function activate(app: JupyterFrontEnd, notebookTracker: INotebookTracker): void {
    app.docRegistry.addWidgetExtension('Notebook', new NotebookSearchExtension(notebookTracker));
}

/**
 * Export the plugin as default.
 */
export default plugin;