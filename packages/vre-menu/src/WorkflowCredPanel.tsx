import { Chip } from '@material-ui/core';
import * as React from 'react';


interface IState {

}

interface WorkflowCredPanelProps {
    credentials: []
}

const DefaultState: IState = {

}


export class WorkflowCredPanel extends React.Component<WorkflowCredPanelProps, IState> {

    state = DefaultState;

    constructor(props: WorkflowCredPanelProps) {
        super(props);
    }

    render(): React.ReactElement {
        return (
            <div>
                {this.props.credentials.map(cred =>
                    <Chip label={cred['name']} onClick={() => {}}/>
                )}
            </div>
        )
    }
}