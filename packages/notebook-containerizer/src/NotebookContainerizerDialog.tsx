import { INotebookModel, INotebookTracker } from '@jupyterlab/notebook';
import { styled, ThemeProvider } from '@material-ui/core';
import * as React from 'react';
import { theme } from './Theme';
import { requestAPI } from '@jupyter_vre/core';

interface IState {
}

export const DefaultState: IState = {
}

const CatalogBody = styled('div')({
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'row',
})

interface NotebookContainerizerDialogProps {

    notebookTracker: INotebookTracker
}

export class NotebookContainerizerDialog extends React.Component<NotebookContainerizerDialogProps> {

    state = DefaultState

    constructor(props: NotebookContainerizerDialogProps) {
        super(props);
    }

    exctractor = async (notebookModel: INotebookModel, _save = false) => {
        try {
            const resp = await requestAPI<any>('nb_containerizer/extract', {
                body: JSON.stringify({
                    notebook: notebookModel.toJSON()
                }),
                method: 'POST'
            });
    
            console.log(resp);
            
        } catch (error) {
            console.log(error);
        }
    }

    componentDidMount(): void {
        
        this.exctractor(this.props.notebookTracker.currentWidget.model);
    }

    render(): React.ReactElement {
        return (
            <ThemeProvider theme={theme}>
                <p className='section-header'>Containerize Notebook</p>
                <CatalogBody>
                </CatalogBody>
            </ThemeProvider>
        )
    }
}