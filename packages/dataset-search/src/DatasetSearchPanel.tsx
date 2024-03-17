import * as React from 'react';
// import { requestAPI } from '@jupyter_vre/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { theme } from './Theme';
import { TextField } from '@material-ui/core';
import Button from '@mui/material/Button';
import Accordion from '@mui/material/Accordion';
import AccordionSummary from '@mui/material/AccordionSummary';
import AccordionDetails from '@mui/material/AccordionDetails';
import Typography from '@mui/material/Typography';
// import DatasetScrollDialog from "./DatasetScrollDialog"
import { requestAPI } from '@jupyter_vre/core';
import DatasetDownload from "./DatasetDownload"

interface DatasetSearchPanelProps {

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


export class DatasetSearchPanel extends React.Component<DatasetSearchPanelProps> {

    state = DefaultState;

    constructor(props: DatasetSearchPanelProps) {
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

    getResults = async () => {
        try{
            const resp = await requestAPI<any>('datasetsearch', {
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
                Dataset Search
              </p>
              <div className={'nb-search-field'}>
                <TextField
                  id="standard-basic"
                  label="Keyword"
                  variant="standard"
                  value={this.state.keyword}
                  onChange={this.onChangeKeyword} />
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
                            <Typography variant="subtitle1">{element['title']}</Typography>
                        </AccordionSummary>
                        <AccordionDetails>
                        <Typography variant="body2" >  
                            <p className={'nb-download-link'}>
                                <a href={element['data_url']} target="_blank">{element['data_url']}</a>
                            </p>      
                        </Typography>
                        <p></p>
                        <br />
                        <br />
                        <Typography variant="subtitle2">
                            <b>Description</b>
                        </Typography>
                        <br />
                        <Typography variant="body1">                            
                            {element['description']}
                        </Typography>
                        <br />
                        <br />
                        <p>
                        <Typography variant="body2">
                            <b>vlab:</b> {element['vlab']}
                            <br />
                            <b>workflow:</b> {element['workflow']}
                            <br />
                            <b>created:</b> {element['created']}
                            <br />
                        </Typography>
                        </p>
                        <br />
                        <br />
                        <br />
                        <DatasetDownload
                            data = {element}/>
                        <p>
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