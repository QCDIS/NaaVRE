import * as React from 'react';
import { requestAPI } from '@jupyter_vre/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { theme } from './Theme';
import { Divider, TextField } from '@material-ui/core';
import Button from '@mui/material/Button';
// import StarRatingComponent from 'react-star-rating-component';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import Rating from '@mui/material/Rating';
// import ReactMarkdown from 'react-markdown'

interface NotebookSearchPanelProps {

}

interface IState {
    keyword: string
    items: [any],
    current_index: number
}

const DefaultState: IState = {
    keyword: '',
    items: [{}],
    current_index: -1
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

    setElementRating = (index: number, rating: number ) => {
        console.log('index: '+index+ ' rating: '+ rating)
        this.state.items[index]['rating'] = rating

    }

    setCurrentIndex = (index: number ) => {
        this.setState({
            current_index: index
        });
    }


    onSearchClick = () => {
        this.getResults();
    }

    onItemClick = (index: number) => {
        console.log(this.state.items[index]);
        console.log(this.state.items);
    }

    onStarClick(nextValue: number, prevValue: number, name: string) {
        console.log(nextValue)
        console.log("name: "+name)
    }

    sendRating2(index: number) {
        console.log("index: "+index)
    }

    sendRating = async () => {
        try{
            const resp = await requestAPI<any>('notebooksearchrating', {
                body: JSON.stringify({
                    keyword: this.state.keyword,
                    notebook:this.state.items[this.state.current_index]
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
                    </div>
                    <div>
                        <div className="accordion">
                            {this.state.items.map((element, index) => (
                            <Accordion >
                            <AccordionSummary>
                                <Typography variant="h6">{element['name']}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                            <Typography variant="body2" >
                            <a href={element['html_url']} target="_blank" >{element['html_url']}</a>
                            <div>
                            <Typography component="legend">Rate for query: {this.state.keyword}</Typography>
                            <Rating
                                name={element['name']}
                                // precision={0.5}
                                defaultValue={1}
                                max={5}
                                onChange={(event, newValue) => {
                                    console.log("Index in newValue: " + newValue);
                                    this.setElementRating(index,newValue)
                                    this.setCurrentIndex(index)
                                }}
                            />
                            <Button
                            onClick={() => {
                                this.sendRating2(index)
                                alert('clicked');
                            }}
                            >
                            Click me
                            </Button>

                            <Button
                                variant="contained"
                                onClick={  this.sendRating }>
                                Send rating
                            </Button>
                            </div>
                            <div>
                            </div>
                            <div>
                                <Button
                                    variant="contained"
                                    >
                                    Download Notebook
                                </Button>
                            </div>
                            </Typography>
                            </AccordionDetails>
                        </Accordion>
                            ))}
                        </div>
                        </div>
                </div>
            </ThemeProvider>
        )
    }
}