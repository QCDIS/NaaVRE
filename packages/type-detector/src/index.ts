import {
    JupyterFrontEnd,
    JupyterFrontEndPlugin
} from '@jupyterlab/application';
import { requestAPI } from '@jupyter_vre/core';
import { ToolbarButton } from '@jupyterlab/apputils';
// import { ToolbarButton, Dialog, showDialog } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import {
    INotebookModel, INotebookTracker, NotebookPanel
} from '@jupyterlab/notebook';
import { DisposableDelegate, IDisposable } from '@lumino/disposable';
import { IOutputAreaModel } from '@jupyterlab/outputarea';
import { Cell } from '@jupyterlab/cells';
// import * as React from 'react';
// import { NotebookContainerizerDialog } from './NotebookContainerizerDialog';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
    activate,
    id: 'toolbar-type-detector',
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

        const typeDetector = async () => {
            // Change button into a spinner and disable
            const button = panel.toolbar.node.querySelector('.type-detector') as HTMLElement;
            button.innerHTML = '<span class="spinner"></span>';
            button.setAttribute('disabled', 'true');

            try{
                // Get contents of currently selected cell
                const currentCell = panel.content.activeCell;
                if (!currentCell) {
                    console.log('No cell selected');
                    return;
                } else if (currentCell.model.type !== 'code') {
                    console.log('Selected cell is not a code cell');
                    return;
                }
                
                // Clear output of currently selected cell
                const cell = panel.content.activeCell;
                const codeCell = cell as Cell & { model: { outputs: IOutputAreaModel } };
                codeCell.model.outputs.clear();
                
                // Get kernel
                const kernel = panel.sessionContext.session?.kernel;
                if (!kernel) {
                    console.log('No kernel found');
                    return;
                }

                const cellContent = currentCell.model.value.text;

                // Call extractor
                const extractedCell = await requestAPI<any>('containerizer/extract', {
                    body: JSON.stringify({
                        save: false,
                        kernel: (await (kernel.info)).implementation,
                        // Cell_index is the index of the cell that is currently selected
                        cell_index: panel.content.activeCellIndex,
                        notebook: _context.model.toJSON()
                    }),
                    method: 'POST'
                });
                console.log(extractedCell);

                const types = extractedCell['types'];
                let source: string = "";

                for (const key in types) {
                    source += `\ntypeof(${key})`;
                }
                
                // Send original source code to kernel
                kernel.requestExecute({ code: cellContent });

                // Send code with typeof() for each variable and retrieve responses.
                const future = kernel.requestExecute({ code: source });
                let vars = Object.keys(types);
                
                future.onIOPub = (msg) => {
                    if (msg.header.msg_type === 'execute_result') {
                        console.log('Execution Result:', msg.content);
                    } else if (msg.header.msg_type === 'display_data') {
                        console.log('Display Data:', msg.content);
                        // Write the content of the message to the output area of the cell
                        const output = {
                            output_type: 'display_data',
                            data: {
                                'text/plain': vars[0] + ': ' + ("data" in msg.content ? msg.content.data['text/html'] : "No data found"),
                            },
                            metadata: {}
                        }

                        codeCell.model.outputs.add(output);
                        // Remove the first element from the vars array
                        vars.shift();
                    } else if (msg.header.msg_type === 'stream') {
                        console.log('Stream:', msg);
                    } else if (msg.header.msg_type === 'error') {
                        console.error('Error:', msg.content);
                        button.innerHTML = '<span class="jp-ToolbarButtonComponent-label">Execute Type Detector</span>';
                        button.removeAttribute('disabled');
                    }
                };

                future.onReply = (msg) => {
                    // If status is 'ok' or 'aborted', then return button
                    if (msg.content.status as string === 'aborted' || msg.content.status as string === 'ok') {
                        button.innerHTML = '<span class="jp-ToolbarButtonComponent-label">Execute Type Detector</span>';
                        button.removeAttribute('disabled');
                    }

                    // Report that type detection was aborted
                    if (msg.content.status as string === 'aborted') {
                        const output = {
                            output_type: 'display_data',
                            data: {
                                'text/plain': 'Type detection was aborted',
                            },
                            metadata: {}
                        }

                        codeCell.model.outputs.add(output);
                    }
                };
                
                console.log(future);

            }catch (error){
                console.log(error);
                alert(String(error).replace('{"message": "Unknown HTTP Error"}',''));
                button.innerHTML = '<span class="jp-ToolbarButtonComponent-label">Execute Type Detector</span>';
                button.removeAttribute('disabled');
            }
        };

        const button = new ToolbarButton({
            className: 'type-detector',
            label: 'Execute Type Detector',
            onClick: typeDetector,
            tooltip: 'Type Detector',
        });

        panel.toolbar.insertItem(10, 'typeDetector', button);
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