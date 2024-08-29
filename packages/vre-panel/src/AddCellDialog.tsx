
import { requestAPI } from '@jupyter_vre/core';
import { CircularProgress, styled, ThemeProvider } from '@material-ui/core';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { green } from '@mui/material/colors';
import * as React from 'react';
import { theme } from './Theme';
import { NotebookPanel } from '@jupyterlab/notebook';


const CatalogBody = styled('div')({
    padding: '20px',
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'column',
})

interface AddCellDialogProps {
    notebook: NotebookPanel,
    closeDialog: () => void
}

interface IState {
    loading: boolean
}

const DefaultState: IState = {
    loading: true
}


export class AddCellDialog extends React.Component<AddCellDialogProps, IState> {

    state = DefaultState;

    handleClose = () => {
        console.log('closing dialog');
        this.props.closeDialog();
    }   

    componentDidMount(): void {
        this.createCell()
    }

    createCell = async () => {
        try {
            const sessionContext = this.props.notebook.context.sessionContext;
            const kernelObject = sessionContext?.session?.kernel; // https://jupyterlab.readthedocs.io/en/stable/api/interfaces/services.kernel.ikernelconnection-1.html#serversettings
            const kernel = (await kernelObject.info).implementation;
            await requestAPI<any>('containerizer/addcell', {
                body: JSON.stringify({
                    kernel
                }),
                method: 'POST'
            });
            this.setState({ loading: false });
        } catch (error) {
            console.log(error);
            alert('Error creating  cell : ' + String(error).replace('{"message": "Unknown HTTP Error"}', ''));
        }
    }

    render(): React.ReactElement {
        return (
            <ThemeProvider theme={theme}>
                <p className='section-header'>Create Cell</p>
                <CatalogBody>
                {!this.state.loading ? (
                    <div style={{display: "flex", flexDirection: "row", alignItems: "center"}}>
                        <div className='cell-submit-box'>
                            <CheckCircleOutlineIcon
                                fontSize='large'
                                sx={{ color: green[500] }}
                            />
                            <p className='cell-submit-text'>
                                The cell has been successfully created!
                            </p>
                            
                        </div>
                    </div>
                    ) :
                    (<div>
                        <CircularProgress />
                        <p>Creating or updating cell ..</p>
                    </div>)
                }
                </CatalogBody>
            </ThemeProvider>
        )
    }
}