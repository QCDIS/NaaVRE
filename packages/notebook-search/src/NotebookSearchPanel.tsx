import * as React from 'react';
import { requestAPI } from '@jupyter_vre/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { theme } from './Theme';
import { TextField } from '@material-ui/core';
import Button from '@mui/material/Button';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
import NotebookScrollDialog from "./NotebookScrollDialog"
import NotebookSendRating from "./NotebookSendRating"
import Autocomplete from "@mui/material/Autocomplete";

interface NotebookSearchPanelProps {

}

interface IState {
    keyword: string
    items: [any],
    current_index: number,
    suggestions: [any]
}

const DefaultState: IState = {
    keyword: '',
    items: [{}],
    current_index: -1,
    suggestions: [{}]
}

export class NotebookSearchPanel extends React.Component<NotebookSearchPanelProps> {


    state = DefaultState;

    constructor(props: NotebookSearchPanelProps) {
        super(props);
    }

    onChangeKeyword = (event: React.ChangeEvent<HTMLInputElement>) => {
        this.getSuggestions();
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

    sendRating = async () => {
        try{
            const resp = await requestAPI<any>('notebook_search_rating', {
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

    getSuggestions = async () => {
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
                <p className={'lw-panel-header'}>
                Notebook Search
                </p>
                <div className={'nb-search-field'}>
                <Autocomplete
                    id="search"
                    freeSolo
                    options={this.state.suggestions.map((option) => option.title)}
                    renderInput={(params) => 
                    <TextField {...params}
                    id="standard-basic"
                    label="Keyword"
                    variant="standard"
                    value={this.state.keyword}
                    onChange={this.onChangeKeyword} />}
                />
                <p>
                    <Button
                    variant="contained"
                    onClick={
                        this.onSearchClick
                        }>
                    Search
                    </Button>
                </p>
                {this.state.items.map((element, index) => (
                    <Accordion >
                        <AccordionSummary>
                            <Typography variant="subtitle1">{element['name']}</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                        <Typography variant="body2" >  
                            <p className={'nb-download-link'}>
                                <a href={element['html_url']} target="_blank">{element['html_url']}</a>
                            </p>      
                        </Typography>
                        <p></p>
                        <br />
                        <br />
                        <Typography variant="subtitle2">
                            <b>Summarization</b>
                        </Typography>
                        <br />
                        <Typography variant="body1">                            
                            {element['summarization']}
                        </Typography>
                        <br />
                        <br />
                        <p>
                        <Typography variant="body2">
                            <b>Summarization Relevance:</b> {element['summarization_relevance']}
                            <br />
                            <b>Summarization Confidence:</b> {element['summarization_confidence']}
                            <br />
                            <b>Notebook source:</b> {element['source']}
                            <br />
                            <b>Number of cells:</b> {element['num_cells']}
                            <br />
                            <b>Langunage:</b> {element['language']}
                        </Typography>
                        </p>
                        <br />
                        <br />
                        <br />
                        <NotebookScrollDialog
                            data = {element}
                            query= {this.state.keyword}/>               
                        <p>
                        <NotebookSendRating
                            data = {element}
                            query= {this.state.keyword}/>
                        </p>                                          
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