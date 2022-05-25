import * as React from 'react';
import { requestAPI } from '@jupyter_vre/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { theme } from './Theme';
import { Divider, TextField } from '@material-ui/core';
import NotebookVirtualizedList from './NotebookVirtualizedList';

interface NotebookSearchPanelProps {

}

interface IState {
    keyword: string
    items: []
}

const DefaultState: IState = {
    keyword: '',
    items: []
}

export class NotebookSearchPanel extends React.Component<NotebookSearchPanelProps> {

    state = DefaultState;

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
            items: resp.hits
        });
    };

    render() {

        return (
            <ThemeProvider theme={theme}>
                <div className={'lifewatch-widget'}>
                    <div className={'lifewatch-widget-content'}>
                        <div>
                            <p className={'lw-panel-header'}>
                                Notebook Search
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
                        <NotebookVirtualizedList
                            items={this.state.items}
                            clickAction={this.onItemClick}
                        />
                    </div>
                </div>
            </ThemeProvider>
        )
    }

}
