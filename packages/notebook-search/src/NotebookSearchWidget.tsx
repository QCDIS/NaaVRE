import { ILabShell, ILayoutRestorer, JupyterFrontEnd, JupyterFrontEndPlugin, LabShell } from "@jupyterlab/application";
import { ReactWidget } from '@jupyterlab/apputils';
import { Widget } from "@lumino/widgets";
import * as React from 'react';
import { NotebookSearchPanel } from "./NotebookSearchPanel";

export interface ILifeWatchVRE {
    widget: Widget;
}

const id = "lifewatch:notebook-search";

export default {
    activate,
    id,
    autoStart: true,
    requires: [ILabShell, ILayoutRestorer]
} as JupyterFrontEndPlugin<ILifeWatchVRE>;

async function activate (
    lab: JupyterFrontEnd,
    labShell: LabShell,
    restorer: ILayoutRestorer,
): Promise<ILifeWatchVRE> {
    
    let widget: ReactWidget;

    lab.started.then(() => {

        widget = ReactWidget.create(
            <NotebookSearchPanel />
        );

        widget.id = "lifewatch/notebook-search"
        widget.title.iconClass = "notebook-search-icon"
        widget.title.caption = 'Notebook Search';
        restorer.add(widget, widget.id);
    });

    lab.restored.then(() => {

        if (!widget.isAttached) {
            labShell.add(widget, 'left');
        }
    });

    return { widget };
}
