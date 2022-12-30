import { NotebookContainerizer2 } from "./NotebookContainerizer2";
import { ILabShell, ILayoutRestorer, JupyterFrontEnd, JupyterFrontEndPlugin, LabShell } from "@jupyterlab/application";
import { ReactWidget } from '@jupyterlab/apputils';
import { Widget } from "@lumino/widgets";
import * as React from 'react';
import { INotebookTracker } from "@jupyterlab/notebook";

export interface ILifeWatchVRE {
    widget: Widget;
}

const id = "lifewatch:notebook-containerizer2";

export default {
    activate,
    id,
    autoStart: true,
    requires: [ILabShell, ILayoutRestorer, INotebookTracker]
} as JupyterFrontEndPlugin<ILifeWatchVRE>;

async function activate (
    lab: JupyterFrontEnd,
    labShell: LabShell,
    restorer: ILayoutRestorer,
    tracker: INotebookTracker
): Promise<ILifeWatchVRE> {
    
    let widget: ReactWidget;

    lab.started.then(() => {

        widget = ReactWidget.create(
            <NotebookContainerizer2
                lab={lab}
                tracker={tracker}
            />
        );

        widget.id = "lifewatch/notebook-containerizer2"
        widget.title.iconClass = "notebook-containerizer2-icon"
        widget.title.caption = 'LifeWatch NotebookContainerizer2';
        restorer.add(widget, widget.id);
    });

    lab.restored.then(() => {

        if (!widget.isAttached) {
            labShell.add(widget, 'left');
        }
    });

    return { widget };
}
