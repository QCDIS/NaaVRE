import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { ToolbarButton } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import {
    INotebookModel, NotebookPanel
} from '@jupyterlab/notebook';
import { DisposableDelegate, IDisposable } from '@lumino/disposable';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
    activate,
    id: 'toolbar-button',
    autoStart: true,
};

export class NotebookSearchExtension
    implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel> {

    createNew(
        panel: NotebookPanel,
        context: DocumentRegistry.IContext<INotebookModel>
    ): IDisposable {

        const searchNotebook = () => {
            console.log('searchNotebook')
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