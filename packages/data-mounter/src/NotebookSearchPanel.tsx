import * as React from 'react';
import { requestAPI } from '@jupyter_vre/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { theme } from './Theme';
import { Divider, TextField } from '@material-ui/core';

interface DataMounterPanelProps {

}

interface IState {
    keyword: string
    items: []
}

const DefaultState: IState = {
    keyword: '',
    items: []
}

export class DataMounterPanel extends React.Component<DataMounterPanelProps> {

    state = DefaultState;

    constructor(props: DataMounterPanelProps) {
        super(props);
    }

    onChangeKeyword = (event: React.ChangeEvent<HTMLInputElement>) => {

        this.setState({
            keyword: event.target.value
        });

        this.getResults();
    }

    onItemClick = (index: number) => {
        console.log(this.state.items[index]);
    }

    getResults = async () => {

        const resp = await requestAPI<any>('notebooksearch', {
            body: JSON.stringify({
                keyword: this.state.keyword
            }),
            method: 'POST'
        });

        this.setState({
            items: resp
        });
    };

    render(): React.ReactElement {

        return (
            <ThemeProvider theme={theme}>
                <div className={'lifewatch-widget'}>
                    <div className={'lifewatch-widget-content'}>
                        <div>
                            <p className={'lw-panel-header'}>
                                Rclone configuration
                            </p>

                        </div>
                        <Divider />
                        <div className={'nb-search-field'}>
                            <TextField
                                id="standard-basic"
                                label="Keyword"
                                variant="standard"
                                value={this.state.keyword}
                                onChange={this.onChangeKeyword} />
                        </div>
                        <Divider />
                    </div>
                </div>
            </ThemeProvider>
        )
    }

}
