
import { Button, styled, TextField, ThemeProvider } from '@material-ui/core';
import { Repository, requestAPI } from '@jupyter_vre/core';
import { Autocomplete, AutocompleteInputChangeReason } from '@mui/material';
import * as React from 'react';
import { theme } from './Theme';
import { Registry } from '@jupyter_vre/core/lib/types';

const CatalogBody = styled('div')({
    padding: '20px',
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'column',
})

interface AddCellDialogProps { }

interface IState {
    repositories: Repository[]
    registries: Registry[]
    selected_repository: string
    selected_registry: string
}

const DefaultState: IState = {
    repositories: [],
    registries: [],
    selected_repository: '',
    selected_registry: ''
}

export class AddCellDialog extends React.Component<AddCellDialogProps, IState> {

    state = DefaultState;

    componentDidMount(): void {
        this.getRepositories();
        this.getRegistries();
    }

    handleConfirm = async () => {
        console.log("confirm");
    }

    allSelected = () => {
        console.log(this.state);
        return (this.state.selected_repository != '' && this.state.selected_registry != '');
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

    getRegistries = async () => {

        const registries = await requestAPI<any>('registries', {
            method: 'GET'
        });

        const items = registries.map((registry: Registry) => (
            { "label": registry.name, "item": registry }
        ));

        this.setState({ registries: items });
    }

    render(): React.ReactElement {

        return (
            <ThemeProvider theme={theme}>
                <p className='section-header'>Create Cell</p>
                <CatalogBody>
                    <p className={'lw-panel-preview'}>Repository</p>
                    <Autocomplete
                        onInputChange={(_event: React.SyntheticEvent<Element, Event>, value: string, _reason: AutocompleteInputChangeReason) => {

                            this.setState({
                                selected_repository: value
                            });
                        }}
                        disablePortal
                        id="combo-box-demo"
                        options={this.state.repositories}
                        sx={{ width: 300, margin: '10px' }}
                        renderInput={(params) => <TextField {...params} label="" />}
                    />
                    <p className={'lw-panel-preview'}>Registry</p>
                    <Autocomplete
                        onInputChange={(_event: React.SyntheticEvent<Element, Event>, value: string, _reason: AutocompleteInputChangeReason) => {

                            this.setState({
                                selected_registry: value
                            });
                        }}
                        disablePortal
                        id="combo-box-demo"
                        options={this.state.registries}
                        sx={{ width: 300, margin: '10px' }}
                        renderInput={(params) => <TextField {...params} label="" />}
                    />
                    <Button variant="contained"
                        style={{ marginTop: '20px' }}
                        onClick={this.handleConfirm}
                        disabled={!this.allSelected()}
                        color="primary">
                        Confirm
                    </Button>
                </CatalogBody>
            </ThemeProvider>
        )
    }
}