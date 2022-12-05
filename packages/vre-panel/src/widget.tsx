import { VREPanel } from "./VREPanel";
import { ILabShell, ILayoutRestorer, JupyterFrontEnd, JupyterFrontEndPlugin, LabShell } from "@jupyterlab/application";
import { ReactWidget } from '@jupyterlab/apputils';
import { Widget } from "@lumino/widgets";
import * as React from 'react';
import { INotebookTracker } from "@jupyterlab/notebook";

export interface ILifeWatchVRE {
    widget: Widget;
}

const id = "lifewatch:vre-plugin";

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
            <VREPanel
                lab={lab}
                tracker={tracker}
            />
        );

        widget.id = "lifewatch/panel"
        widget.title.iconClass = "left-panel-icon"
        widget.title.caption = 'LifeWatch Panel';
        restorer.add(widget, widget.id);
    });

    lab.restored.then(() => {

        if (!widget.isAttached) {
            labShell.add(widget, 'left');
        }
    });

    return { widget };
}
