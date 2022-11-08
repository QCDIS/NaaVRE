import { ILabShell, ILayoutRestorer, JupyterFrontEnd, JupyterFrontEndPlugin, LabShell } from "@jupyterlab/application";
import { ReactWidget } from '@jupyterlab/apputils';
import { Widget } from "@lumino/widgets";
import * as React from 'react';
import { DatameshPanel as DatameshPanel } from "./datameshPanel";

export interface ILifeWatchVRE {
    widget: Widget;
}

const id = "lifewatch:datamesh";

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
            <DatameshPanel />
        );

        widget.id = "lifewatch/datamesh"
        widget.title.iconClass = "datamesh-icon"
        widget.title.caption = 'Datamesh';
        restorer.add(widget, widget.id);
    });

    lab.restored.then(() => {

        if (!widget.isAttached) {
            labShell.add(widget, 'left');
        }
    });

    return { widget };
}
