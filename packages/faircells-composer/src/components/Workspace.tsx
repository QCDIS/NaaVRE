import Box from '@mui/material/Box';
import * as React from 'react';

export class Workspace extends React.Component {

    render() {
        return (
            <Box sx={{ background: 'white', height: 500, width: 250, transform: 'translateZ(0px)', flexGrow: 1, position: 'absolute', top: 20, left: 20 }}>
                <div>Workspace</div>
            </Box>
        )
    }
}