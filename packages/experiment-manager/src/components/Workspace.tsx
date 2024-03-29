import * as React from 'react';
import { VRECell } from '@jupyter_vre/core';
import { WorkspaceItem } from './WorkspaceItem';

interface IState {
    workspace_elements: Map<string, VRECell>
}

export const DefaultState: IState = {
    workspace_elements: new Map<string, VRECell>()
}

export class Workspace extends React.Component {

    state = DefaultState;

    addElement = (element: VRECell) => {

        let currElements = this.state.workspace_elements;
        currElements.set(element.node_id, element);
        this.setState({ workspace_elements: currElements })
    }

    removeElement = (key: string) => {

        let currElements = this.state.workspace_elements;
        currElements.delete(key);
        this.setState({ workspace_elements: currElements })
    }

    hasElement = (element: VRECell) => {
        return this.state.workspace_elements.has(element.node_id);
    }

    getElement = (nodeId: string) => {
        return this.state.workspace_elements.get(nodeId); 
    }

    renderItems(map: Map<string, VRECell>): JSX.Element[] {

        const items: JSX.Element[] = [];

        map.forEach((value, key) => {

            let nodes = value.chart_obj.nodes;
            let element = nodes[Object.keys(nodes)[0]];

            items.push(
                <WorkspaceItem
                    key={key}
                    itemKey={key}
                    type={element['type']}
                    ports={element['ports']}
                    properties={element['properties']}
                    itemDeleteAction={this.removeElement}
                />
            );
        });

        return items;
    }

    render() {
        return (
          <div style={{ flex: 'auto', minHeight: '200px' }}>
                <p className='section-header'>Workspace</p>
                {this.state.workspace_elements.size == 0 ?
                    (<div className={'empty-workspace'}>
                        The workspace is empty, click on 'Cells catalog' to add cells.
                    </div>)
                    : (
                        <div className={'workspace-items-container'}>
                            {this.renderItems(this.state.workspace_elements)}
                        </div>
                    )
                }
            </div>
        )
    }
}