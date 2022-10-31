import * as React from 'react';
import { requestAPI } from '@jupyter_vre/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { theme } from './Theme';
import { Divider, TextField } from '@material-ui/core';
import NotebookVirtualizedList from './NotebookVirtualizedList';
import Button from '@mui/material/Button';
import StarRatingComponent from 'react-star-rating-component';

interface NotebookSearchPanelProps {

}

interface IState {
    keyword: string
    items: []
    rating: number
}

const DefaultState: IState = {
    keyword: '',
    items: [],
    rating: 1
}

export class NotebookSearchPanel extends React.Component<NotebookSearchPanelProps> {

    state = DefaultState;

    constructor(props: NotebookSearchPanelProps) {
        super(props);
    }

    onChangeKeyword = (event: React.ChangeEvent<HTMLInputElement>) => {

        this.setState({
            keyword: event.target.value
        });
        
    }

    onSearchClick = () => {
        this.getResults();
    }

    onItemClick = (index: number) => {
        console.log(this.state.items[index]);
    }

    onStarClick(nextValue: any, prevValue: any, name: any) {
        console.log(nextValue)
        this.setState({rating: nextValue});
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
        const { rating } = this.state;
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
                                <Button 
                                    variant="contained"
                                    onClick={
                                        this.onSearchClick
                                      }>
                                    Search
                                </Button>
                        </div>
                        <Divider />
                        <NotebookVirtualizedList
                            items={this.state.items}
                            clickAction={this.onItemClick}
                        />
                    </div>
                    <div>
                        <h2>Rating from state: {rating}</h2>
                        <StarRatingComponent 
                        name="rate1" 
                        starCount={5}
                        value={rating}
                        onStarClick={this.onStarClick.bind(this)}

                        />
                    </div>
                </div>
            </ThemeProvider>
        )
    }

}
