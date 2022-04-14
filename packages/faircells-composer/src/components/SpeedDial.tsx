import * as React from 'react';
import Box from '@mui/material/Box';
import SpeedDial from '@mui/material/SpeedDial';
import SpeedDialIcon from '@mui/material/SpeedDialIcon';
import SpeedDialAction from '@mui/material/SpeedDialAction';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import AutoStoriesIcon from '@mui/icons-material/AutoStories';

interface BasicSpeedDialProps {
    handleDialSelection: (operation: string) => void
}

export default function BasicSpeedDial({ handleDialSelection }: BasicSpeedDialProps) {

    const actions = [
        { icon: <AutoStoriesIcon />, name: 'Open Catalog', operation: 'open-catalog' },
        { icon: <FileUploadIcon />, name: 'Export Workflow', operation: 'export-workflow' }
    ];

    return (
        <Box sx={{ height: 320, transform: 'translateZ(0px)', flexGrow: 1, position: 'absolute', bottom: '10px', right: '10px' }}>
            <SpeedDial
                ariaLabel="SpeedDial basic example"
                sx={{ position: 'absolute', bottom: 16, right: 16 }}
                icon={<SpeedDialIcon />}
            >
                {actions.map((action) => (
                    <SpeedDialAction
                        key={action.name}
                        icon={action.icon}
                        tooltipTitle={action.name}
                        onClick={() => {
                            handleDialSelection(action.operation)
                        }}
                    />
                ))}
            </SpeedDial>
        </Box>
    );
}
