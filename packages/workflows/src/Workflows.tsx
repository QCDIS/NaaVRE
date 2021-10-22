import * as React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';

const Workflows = (): JSX.Element => {
    return (
        <div>Workflows</div>
    );
};

export class WorkflowsWidget extends ReactWidget {

    constructor() {
        super();
        this.addClass('vre-workflows');
    }

    render(): JSX.Element {
        return <Workflows />;
    }
}