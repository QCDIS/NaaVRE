import * as React from 'react';
import { theme } from './Theme';
import { ThemeProvider } from '@material-ui/core/styles';
import { JupyterFrontEnd } from '@jupyterlab/application';
import { INotebookTracker, NotebookPanel } from '@jupyterlab/notebook';
import { NotebookTracker } from './NotebookTracker'
import { Divider } from '@material-ui/core';


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
                            <NotebookTracker
                                notebook={this.getActiveNotebook()}
                            />
                        </div>
                    </div>
                </div>
            </ThemeProvider>
        );
    }
} 