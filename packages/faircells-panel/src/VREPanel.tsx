import * as React from 'react';
import { theme } from './Theme';
import { ThemeProvider } from '@material-ui/core/styles';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { CellTracker } from './CellTracker'
import { Dialog, showDialog } from '@jupyterlab/apputils';
import { Divider } from '@material-ui/core';
import { requestAPI } from '@jupyter_vre/core';


interface IProps {
    lab: JupyterFrontEnd;
    tracker: INotebookTracker;
}

interface IState {
    notebook_path   : string
    loading         : boolean
}

export const DefaultState: IState = {
    notebook_path   : '',
    loading         : false
}

export class VREPanel extends React.Component<IProps> {

    state = DefaultState

    getActiveNotebook = () => {
        return this.props.tracker.currentWidget;
    };

    handleNotebookChanged = async (
        tracker: INotebookTracker,
        notebook: NotebookPanel
    ) => {
        if (notebook) {
            this.setState({ notebook_path: notebook.context.path });
        }
    };

    componentDidMount = () => {
        this.props.tracker.currentChanged.connect(this.handleNotebookChanged, this);
        if (this.props.tracker.currentWidget instanceof NotebookPanel) {
            this.setState({ notebook_path: this.props.tracker.currentWidget.context.path });
        }
    };

    componentDidUpdate = () => {
        console.log('Component updated');
    }

    addToCatalog = async () => {
        if (!this.state.loading) {

            this.setState({ loading: true });

            try {

                await requestAPI<any>('containerizer/addcell', {
                    body: JSON.stringify({}),
                    method: 'POST'
                });
                setTimeout(() => {
                    this.setState({ loading: false });
                    showDialog({
                        title: 'Local Catalog',
                        body: (
                          <p>
                            Cell successfully added to the catalog
                          </p>
                        ),
                        buttons: [Dialog.okButton()]
                    });
                }, 1500);
            }

            catch (error) {
                console.log(error);
                alert('Error adding cell to catalog: '+ String(error).replace('{"message": "Unknown HTTP Error"}',''));
                this.setState({ loading: false });
            }
        }
    }

    render() {
        return (
            <ThemeProvider theme={theme}>
                <div className={'lifewatch-widget'}>
                    <div className={'lifewatch-widget-content'}>
                        <div>
                            <p className={'lw-panel-header'}>
                                Component containerizer
                            </p>
                            <Divider />
                            <div>
                                <p className={'lw-panel-curr-nb'}>
                                    {this.state.notebook_path}
                                </p>
                            </div>
                            <Divider />
                        </div>
                        <div style={{ marginTop: 5 }}>
                            <CellTracker
                                notebook={this.getActiveNotebook()}
                            />
                        </div>
                    </div>
                </div>
            </ThemeProvider>
        );
    }
} 