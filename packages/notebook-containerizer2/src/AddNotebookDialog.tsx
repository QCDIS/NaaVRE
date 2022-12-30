
import { requestAPI } from '@jupyter_vre/core';
import { CircularProgress, styled, ThemeProvider } from '@material-ui/core';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { green } from '@mui/material/colors';
import * as React from 'react';
import { theme } from './Theme';

const CatalogBody = styled('div')({
    padding: '20px',
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'column',
})

interface AddNotebookDialogProps { }

interface IState {
    loading: boolean
}

const DefaultState: IState = {
    loading: true
}

export class AddNotebookDialog extends React.Component<AddNotebookDialogProps, IState> {

    state = DefaultState;

    componentDidMount(): void {
        this.createNotebook()
    }

    createNotebook = async () => {
        try {

            await requestAPI<any>('containerizer/addcell', {
                body: JSON.stringify({}),
                method: 'POST'
            });

            this.setState({ loading: false });

        } catch (error) {
            console.log(error);
            alert('Error creating  notebook : ' + String(error).replace('{"message": "Unknown HTTP Error"}', ''));
        }
    }

    render(): React.ReactElement {

        return (
            <ThemeProvider theme={theme}>
                
                <p className='section-header'>Create notebook</p>
                <CatalogBody>
                {!this.state.loading ? (
                    <div style={{display: "flex", flexDirection: "row", alignItems: "center"}}>
                        <div className='notebook-submit-box'>
                            <CheckCircleOutlineIcon
                                fontSize='large'
                                sx={{ color: green[500] }}
                            />
                            <p className='notebook-submit-text'>
                                The notebook has been successfully created!
                            </p>
                        </div>
                    </div>
                    ) :
                    (<div>
                        <CircularProgress />
                        <p>Creating or updating notebook ..</p>
                    </div>)
                }
                </CatalogBody>
            </ThemeProvider>
        )
    }
}