
import { styled, TextField, ThemeProvider } from '@material-ui/core';
import { Repository, requestAPI } from '@jupyter_vre/core';
import { Autocomplete } from '@mui/material';
import * as React from 'react';
import { theme } from './Theme';

const CatalogBody = styled('div')({
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'row',
})

interface AddCellDialogProps { }

interface IState {
    repositories    : Repository[]
}

const DefaultState: IState = {
    repositories    : []
}

export class AddCellDialog extends React.Component<AddCellDialogProps, IState> {

    state = DefaultState;

    componentDidMount(): void {
        this.getRepositories();
    }

    getRepositories = async () => {

        const repositories = await requestAPI<any>('repositories', {
            method: 'GET'
        });

        const items = repositories.map((repo: Repository) => (
            { "label": repo.name, "item": repo }
        ));

        this.setState({ repositories: items });
    }

    render(): React.ReactElement {

        return (
            <ThemeProvider theme={theme}>
                <p className='section-header'>Create Cell</p>
                <CatalogBody>
                <p className={'lw-panel-preview'}>Repository</p>
                <Autocomplete
                            disablePortal
                            id="combo-box-demo"
                            options={this.state.repositories}
                            sx={{ width: 300, margin: '10px' }}
                            renderInput={(params) => <TextField {...params} label="" />}
                        />
                </CatalogBody>
            </ThemeProvider>
        )
    }
}