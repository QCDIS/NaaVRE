import Box from '@mui/material/Box';
import * as React from 'react';
import { FairCell } from '@jupyter_vre/core';

interface CellEditorProps {
    cell: FairCell
}

export class CellEditor extends React.Component<CellEditorProps> {

    constructor(props: CellEditorProps) {
        super(props);
    }

    render() {
        return (
            <Box sx={{ borderRadius: '15px', boxShadow: '1px 1px lightgrey', background: 'white', height: 500, width: 500, transform: 'translateZ(0px)', flexGrow: 1, position: 'absolute', top: 20, right: 20 }}>
                <p className='cell-editor section-header'>{this.props.cell.title}</p>
                <div >
                    
                </div>
            </Box>
        )
    }
}