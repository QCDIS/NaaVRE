import Box from '@mui/material/Box';
import * as React from 'react';
import { FairCell } from '../faircell';
import { WorkspaceItem } from './WorkspaceItem';

interface IState {
    workspace_elements: FairCell[]
}

export const DefaultState: IState = {
    workspace_elements: []
}

export class Workspace extends React.Component {

    state = DefaultState;

    addElement = (element: FairCell) => {

        let currElements = this.state.workspace_elements;
        currElements.push(element);
        this.setState({ workspace_elements: currElements })
        console.log(this.state);
    }

    render() {
        return (
            <Box sx={{ background: 'white', height: 500, width: 250, transform: 'translateZ(0px)', flexGrow: 1, position: 'absolute', top: 20, left: 20 }}>
                <p className='section-header'>Workspace</p>
                <div className={'workspace-items-container'}>
                    {this.state.workspace_elements.map((value, _index) => {
                        let nodes = value['chart_obj']['nodes']
                        let element = nodes[Object.keys(nodes)[0]]
                        return (
                            <WorkspaceItem
                                type={element['type']}
                                ports={element['ports']}
                                properties={element['properties']}
                            />
                        )
                    })}
                </div>
            </Box>
        )
    }
}