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

    onStarClick(nextValue: number, prevValue: number, name: string) {
        console.log(nextValue)
        this.setState({rating: nextValue});
        this.state.rating = nextValue
        console.log(this.state.rating)
    }

    sendrating = async () => {
        console.log('Query: ',this.state.keyword)
        console.log('Rating: ',this.state.rating)     
        try{
            const resp = await requestAPI<any>('notebooksearchrating', {
                body: JSON.stringify({
                    keyword: this.state.keyword,
                    rating: this.state.rating
                }),
                method: 'POST'
            });
            console.log('resp: ',resp)
        }catch (error){
            console.log(error);
            alert(String(error).replace('{"message": "Unknown HTTP Error"}', ''));
        }
    };

    getResults = async () => {        
        try{
            const resp = await requestAPI<any>('notebooksearch', {
                body: JSON.stringify({
                    keyword: this.state.keyword
                }),
                method: 'POST'
            });

            this.setState({
                items: resp
            });
        }catch (error){
            console.log(error);
            alert(String(error).replace('{"message": "Unknown HTTP Error"}', ''));
        }
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
                        <h2>Rating from query: {this.state.keyword}</h2>
                        <StarRatingComponent 
                        name="rate1" 
                        starCount={5}
                        value={rating}
                        onStarClick={this.onStarClick.bind(this)}
                        />
                        <Button 
                            variant="contained"
                            onClick={ this.sendrating }>
                            Send rating
                        </Button>
                    </div>
                </div>
            </ThemeProvider>
        )
    }

}
