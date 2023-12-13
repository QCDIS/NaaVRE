import Box from '@mui/material/Box';
import * as React from 'react';
import { WorkspaceItem } from './WorkspaceItem';

export class Visualization extends React.Component {

    render() {
        return (
            <Box sx={{ boxShadow: '1px 1px lightgrey', background: 'white', height: '30%', width: 250, transform: 'translateZ(0px)', flexGrow: 1, position: 'relative', bottom: 0, left: 0}}>
                <p className='section-header'>
                    <span title="Accepts a list as input." style={{ borderBottom: '1px dotted black' }}>
                        Visualization
                    </span>
                </p>
                <div>
                    <WorkspaceItem
                        key={'visualizer'}
                        itemKey={'visualizer'}
                        type={'visualizer'} ports={{
                            visualizer_source: {
                                id: 'visualizer_source',
                                type: 'left',
                                properties: {
                                    special_node: 1,
                                    color: '#000000'
                                }
                            }
                        }}
                        properties={{
                            'title': 'Visualizer',
                            'scalingFactor': 1
                        }}
                    />
                </div>
            </Box>
        )
    }
}
