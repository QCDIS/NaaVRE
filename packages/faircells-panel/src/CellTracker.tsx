import { FlowChart, IChart } from "@mrblenny/react-flow-chart";
import { cloneDeep, mapValues } from 'lodash'
import * as actions from "@mrblenny/react-flow-chart/src/container/actions";
import * as React from 'react';
import { requestAPI } from '@jupyter_vre/core';
import { INotebookModel, Notebook, NotebookPanel } from '@jupyterlab/notebook';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { Cell } from '@jupyterlab/cells';
import Table from '@material-ui/core/Table';
import { theme } from './Theme';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import { FormControl, MenuItem, Select, TableBody, ThemeProvider } from "@material-ui/core";
import { NodeInnerCustom, PortCustom } from '@jupyter_vre/chart-customs';

const defaultChart: IChart = { 
    offset: {
        x: 0,
        y: 0,
    },
    scale: 1,
    nodes: {},
    links: {},
    selected: {},
    hovered: {}
}

interface IProps {
    notebook: NotebookPanel;
}

interface IState {
    activeCellIndex : number,
    chart           : IChart,
}


type SaveState = 'started' | 'completed' | 'failed';

export class CellTracker extends React.Component<IProps, IState> {

    state = cloneDeep(defaultChart);
    currCellIndex = 0;
    currNodeId: string = null;

    stateActions = mapValues(actions, (func: any) =>
        (...args: any) => this.setState(func(...args))) as typeof actions


    typesUpdate = async (event: React.ChangeEvent<{ name?: string; value: unknown; }>, port: string) => {

        const resp = await requestAPI<any>('types', {
            body: JSON.stringify({
                port: port,
                type: event.target.value
            }),
            method: 'POST'
        });

        console.log(resp);
    };

    exctractor = async (notebookModel: INotebookModel, save = false) => {
            
        const resp = await requestAPI<any>('extractor', {
            body: JSON.stringify({
                save: save,
                cell_index: this.currCellIndex,
                notebook: notebookModel.toJSON()
            }),
            method: 'POST'
        });

        this.currNodeId = resp['node_id'];
        this.setState(resp['chart']);
    }

    onActiveCellChanged = (notebook: Notebook, activeCell: Cell) => {
        this.currCellIndex = notebook.activeCellIndex;
        this.exctractor(this.props.notebook.model);
    };

    handleSaveState = (context: DocumentRegistry.Context, state: SaveState) => {
        if (state === 'completed') {
            this.exctractor(this.props.notebook.model);
        }
    };

    connectAndInitWhenReady = (notebook: NotebookPanel) => {
        notebook.context.ready.then(() => {
            this.props.notebook.content.activeCellChanged.connect(this.onActiveCellChanged);
            this.props.notebook.context.saveState.connect(this.handleSaveState);
            this.currCellIndex = notebook.content.activeCellIndex
        });
    };

    componentDidMount = () => {
        if (this.props.notebook) {
            this.connectAndInitWhenReady(this.props.notebook);
        }
    }

    componentDidUpdate = async (
        prevProps: Readonly<IProps>,
        prevState: Readonly<IState>,
    ) => {
        
        const preNotebookId = prevProps.notebook ? prevProps.notebook.id : '';
        const notebookId = this.props.notebook ? this.props.notebook.id : '';

        if (preNotebookId !== notebookId) {

            if (prevProps.notebook) {
                prevProps.notebook.content.activeCellChanged.disconnect(this.onActiveCellChanged);
            }
            if (this.props.notebook) {
                this.connectAndInitWhenReady(this.props.notebook);
            }
        }
    }

    render() {
        return (
            <ThemeProvider theme={theme}>
                <div>
                    <div className={'lw-panel-editor'}>
                        <FlowChart
                            chart={this.state}
                            callbacks={this.stateActions}
                            Components={{
                                NodeInner   : NodeInnerCustom,
                                Port        : PortCustom
                            }}
                        />
                    </div>
                    {this.currNodeId ? (
                        <div>
                        <p className={'lw-panel-preview'}>Inputs and Outputs</p>
                        <TableContainer component={Paper} className={'lw-panel-table'}>
                            <Table aria-label="simple table">
                                <TableBody>
                                {this.state.nodes[this.currNodeId].properties['vars'].map((variable: any) => (
                                    <TableRow key={variable.name}>
                                        <TableCell component="th" scope="row">
                                            <p style={{color: variable.color, fontSize: "1em"}}>{variable.name}</p>
                                        </TableCell>
                                        <TableCell component="th" scope="row">
                                            {variable.direction}
                                        </TableCell>
                                        <TableCell component="th" scope="row">
                                            <FormControl fullWidth>
                                                <Select
                                                    labelId="io-types-select-label"
                                                    id="io-types-select"
                                                    label="Type"
                                                    onChange={(event) => {this.typesUpdate(event, variable.name)}}
                                                >
                                                    <MenuItem value={'int'}>Integer</MenuItem>
                                                    <MenuItem value={'float'}>Float</MenuItem>
                                                    <MenuItem value={'str'}>String</MenuItem>
                                                    <MenuItem value={'list'}>List</MenuItem>
                                                </Select>
                                            </FormControl>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                            </Table>
                        </TableContainer>
                        <p className={'lw-panel-preview'}>Parameters</p>
                        <TableContainer component={Paper} className={'lw-panel-table'}>
                            <Table aria-label="simple table">
                                <TableBody>
                                {this.state.nodes[this.currNodeId].properties['params'].map((param: any) => (
                                    <TableRow key={param}>
                                        <TableCell component="th" scope="row">
                                            {param}
                                        </TableCell>
                                        <TableCell component="th" scope="row">
                                            <FormControl fullWidth>
                                                <Select
                                                    labelId="param-types-select-label"
                                                    id="param-types-select"
                                                    label="Type"
                                                    onChange={(event) => {this.typesUpdate(event, param)}}
                                                >
                                                    <MenuItem value={'int'}>Integer</MenuItem>
                                                    <MenuItem value={'float'}>Float</MenuItem>
                                                    <MenuItem value={'str'}>String</MenuItem>
                                                    <MenuItem value={'list'}>List</MenuItem>
                                                </Select>
                                            </FormControl>
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                            </Table>
                        </TableContainer>
                        <p className={'lw-panel-preview'}>Dependencies</p>
                        <TableContainer component={Paper} className={'lw-panel-table'}>
                            <Table aria-label="simple table">
                                <TableBody>
                                {this.state.nodes[this.currNodeId].properties['deps'].map((dep: any) => (
                                    <TableRow key={dep}>
                                        <TableCell component="th" scope="row">
                                            {dep}
                                        </TableCell>
                                    </TableRow>
                                ))}
                            </TableBody>
                            </Table>
                        </TableContainer>
                        </div>
                    ) :(
                        <TableContainer></TableContainer>
                    )}
                    </div>
            </ThemeProvider>
        );
    }
}