
import { styled, ThemeProvider } from '@material-ui/core';
import * as React from 'react';
import { theme } from './Theme';
const CatalogBody = styled('div')({
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'row',
})

interface AddCellDialogProps { }

interface IState {

}

const DefaultState: IState = {

}

export class AddCellDialog extends React.Component<AddCellDialogProps, IState> {

    state = DefaultState;

    render(): React.ReactElement {

        return (
            <ThemeProvider theme={theme}>
                <p className='section-header'>Create Cell</p>
                <CatalogBody>
                    
                </CatalogBody>
            </ThemeProvider>
        )
    }
}