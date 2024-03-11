import * as React from 'react';
import { WorkspaceItem } from './WorkspaceItem';

export class Visualization extends React.Component {

    render() {
        return (
            <div>
                <p className='section-header'>
                    <span title="Accepts a list as input." style={{ borderBottom: '1px dotted black' }}>
                        Visualization
                    </span>
                </p>
                <div>
                    <WorkspaceItem
                        key={'visualizer'}
                        itemKey={'visualizer'}
                        type={'visualizer'} 
                        ports={
                            {
                                hostname: {
                                    id: 'hostname',
                                    type: 'left',
                                    properties: {
                                        color: '#000000'
                                    }
                                },
                                username: {
                                    id: 'username',
                                    type: 'left',
                                    properties: {
                                        color: '#000000'
                                    }
                                },
                                password : {
                                    id: 'password',
                                    type: 'left',
                                    properties: 
                                    {
                                        color: '#000000'
                                    }
                                },
                                remote : {
                                    id: 'remote',
                                    type: 'left',
                                    properties: 
                                    {
                                        color: '#000000'
                                    }
                                },
                                num : {
                                    id: 'num',
                                    type: 'left',
                                    properties: 
                                    {
                                        color: '#000000'
                                    }
                                },
                                mode : {
                                    id: 'mode',
                                    type: 'left',
                                    properties: 
                                    {
                                        color: '#000000'
                                    }
                                },
                                output : {
                                    id: 'output',
                                    type: 'left',
                                    properties: 
                                    {
                                        color: '#000000'
                                    }
                                }
                            }
                        }
                        properties={
                        {
                            'title': 'Visualizer',
                            'scalingFactor': 1
                        }
                        }
                    />
                </div>
            </div>
        )
    }
}
