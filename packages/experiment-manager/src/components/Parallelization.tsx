import * as React from 'react';
import { WorkspaceItem } from './WorkspaceItem';

export class Parallelization extends React.Component {

    render() {
        return (
            <div>
                <p className='section-header'>Parallelization</p>
                <div>
                    <WorkspaceItem
                        key={'splitter'}
                        itemKey={'splitter'}
                        type={'splitter'} 
                        ports={
                            {
                                splitter_source: 
                                {
                                    id: 'splitter_source',
                                    type: 'left',
                                    properties: {
                                    special_node: 1,
                                    color: '#000000'
                                }
                            },
                            splitter_target: 
                            {
                                id: 'splitter_target',
                                type: 'right',
                                properties: {
                                    special_node: 1,
                                    color: '#000000'
                                }
                            }
                        }
                    }
                        properties={{
                            'title': 'Splitter',
                            'scalingFactor': 1
                        }}
                    />
                    <WorkspaceItem
                        key={'merger'}
                        itemKey={'merger'}
                        type={'merger'} ports={{
                            merger_source: {
                                id: 'merger_source',
                                type: 'left',
                                properties: {
                                    special_node: 1,
                                    color: '#000000'
                                }
                            },
                            merger_target: {
                                id: 'merger_target',
                                type: 'right',
                                properties: {
                                    special_node: 1,
                                    color: '#000000'
                                }
                            }
                        }}
                        properties={{
                            'title': 'Merger',
                            'scalingFactor': 1
                        }}
                    />
                </div>
            </div>
        )
    }
}
