import * as React from 'react';
import Box from '@mui/material/Box';
import SpeedDial from '@mui/material/SpeedDial';
import SpeedDialIcon from '@mui/material/SpeedDialIcon';
import SpeedDialAction from '@mui/material/SpeedDialAction';
import FileUploadIcon from '@mui/icons-material/FileUpload';
import CallSplitIcon from '@mui/icons-material/CallSplit';
import AutoStoriesIcon from '@mui/icons-material/AutoStories';
import { makeStyles } from '@material-ui/core';

interface BasicSpeedDialProps {
    handleDialSelection: (operation: string) => void
}

const actions = [
    { icon: <AutoStoriesIcon />, name: 'Explore Catalogs', operation: 'explore-catalogs' },
    { icon: <FileUploadIcon />, name: 'Export Workflow', operation: 'export-workflow' },
    { icon: <CallSplitIcon />, name: 'Parallelization', operation: 'parallelization' }
];

const useStyles = makeStyles(() => ({
    staticTooltipLabel: {
        width: "200px !important"
    }
}));

export default function BasicSpeedDial({ handleDialSelection }: BasicSpeedDialProps) {

    const classes = useStyles()

    return (
        <Box sx={{ height: 320, transform: 'translateZ(0px)', flexGrow: 1, position: 'absolute', bottom: 16, right: 16 }}>
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
                        tooltipOpen
                        classes={classes}
                        onClick={() => {
                            handleDialSelection(action.operation)
                        }}
                    />
                ))}
            </SpeedDial>
        </Box>
    );
}
