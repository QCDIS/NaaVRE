import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { Dialog, ReactWidget, showDialog, ToolbarButton } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import {
    INotebookModel, NotebookPanel
} from '@jupyterlab/notebook';
import { DisposableDelegate, IDisposable } from '@lumino/disposable';
import * as React from 'react';
import { NotebookSearchPanel } from './NotebookSearchPanel';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
    activate,
    id: 'toolbar-button',
    autoStart: true,
};

const NotebookSearchDialogOptions: Partial<Dialog.IOptions<any>> = {
    title: '',
    body: ReactWidget.create(
        <NotebookSearchPanel />
    ) as Dialog.IBodyWidget<any>,
    buttons: []
};

export class NotebookSearchExtension
    implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {

    createNew(
        panel: NotebookPanel,
        context: DocumentRegistry.IContext<INotebookModel>
    ): IDisposable {

        const searchNotebook = () => {

            showDialog(NotebookSearchDialogOptions);
        };

        const button = new ToolbarButton({
            className: 'notebook-search',
            label: 'Notebooks Search',
            onClick: searchNotebook,
            tooltip: 'Notebooks Search',
        });

        panel.toolbar.insertItem(10, 'searchNotebooks', button);
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
function activate(app: JupyterFrontEnd): void {
    app.docRegistry.addWidgetExtension('Notebook', new NotebookSearchExtension());
}

/**
 * Export the plugin as default.
 */
export default plugin;