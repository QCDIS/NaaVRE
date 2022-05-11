import { styled, ThemeProvider } from '@material-ui/core';
import * as React from 'react';
import { theme } from '../Theme';

const CatalogBody = styled('div')({
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'row',
})

export class ParallelizationDialog extends React.Component {

    render(): React.ReactNode {
        
        return (
            <ThemeProvider theme={theme}>
                <p className='section-header'>Parallelization Operators</p>
                <CatalogBody>

                </CatalogBody>
            </ThemeProvider>
        )
    }
}