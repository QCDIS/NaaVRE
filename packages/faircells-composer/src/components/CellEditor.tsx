import Box from '@mui/material/Box';
import * as React from 'react';
import { FairCell } from '../faircell';

interface IState {
    selected_cell: FairCell
}

export const DefaultState: IState = {
    selected_cell: null
}

export class CellEditor extends React.Component {

    state = DefaultState;

    render() {
        return (
            <Box sx={{ boxShadow: '1px 1px lightgrey', background: 'white', height: 500, width: 250, transform: 'translateZ(0px)', flexGrow: 1, position: 'absolute', top: 20, right: 20 }}>
                <p className='section-header'>Cell Editor</p>
                {this.state.selected_cell == null ? 
                (<div className={'empty-workspace'}>
                    Click on a cell inside the canvas to access its property in the editor.
                </div>) 
                : (
                    <div></div>
                )
                }
            </Box>
        )
    }
}