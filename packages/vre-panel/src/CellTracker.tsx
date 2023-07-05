import * as React from 'react';
import { requestAPI, VRECell, CellPreview } from '@jupyter_vre/core';
import { INotebookModel, Notebook, NotebookPanel } from '@jupyterlab/notebook';
import { ReactWidget, Dialog, showDialog } from '@jupyterlab/apputils';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { Cell } from '@jupyterlab/cells';
import Table from '@material-ui/core/Table';
import { theme } from './Theme';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import { Button, FormControl, MenuItem, Select, TableBody, TextField, ThemeProvider } from "@material-ui/core";
import { Autocomplete } from '@mui/material';
import { AddCellDialog } from './AddCellDialog';

interface IProps {
    notebook: NotebookPanel;
}

interface IState {

    loading: boolean
    baseImageSelected: boolean
    currentCellIndex: number
    currentCell: VRECell
    typeSelections: { [type: string]: boolean }
}

const DefaultState: IState = {

    loading: false,
    baseImageSelected: false,
    currentCellIndex: -1,
    currentCell: null,
    typeSelections: {}
}

type SaveState = 'started' | 'completed' | 'failed';

const baseImages = [
    { label: "miniconda3", id: "qcdis/miniconda3" },
    { label: "Laserfarm", id: "qcdis/miniconda3-pdal" },
    { label: "vol2bird", id: "qcdis/python-vol2bird" },
    { label: "distributed-learning", id: "qcdis/miniconda3-distributed-learning" },
    { label: "MULTIPLY", id: "qcdis/miniconda3-multiply" },
    { label: "Jupyter R Notebook", id: "jupyter/r-notebook:70178b8e48d7"}
]

export class CellTracker extends React.Component<IProps, IState> {

    state = DefaultState;
    cellPreviewRef: React.RefObject<CellPreview>;

    constructor(props: IProps) {
        super(props);
        this.cellPreviewRef = React.createRef();
    }

    handleCreateCell = async () => {
        const AddCellDialogOptions: Partial<Dialog.IOptions<any>> = {
            title: '',
            body: ReactWidget.create(
                <AddCellDialog notebook={this.props.notebook}/>
            ) as Dialog.IBodyWidget<any>,
            buttons: []
        };
        showDialog(AddCellDialogOptions)
    }

    allTypesSelected = () => {
        console.log('allTypesSelected' )
        for (let key in this.state.typeSelections) {
            console.log(key + ": " + this.state.typeSelections[key]);
          }

        console.log('Object.values(this.state.typeSelections).length: '+Object.values(this.state.typeSelections).length)
        if (Object.values(this.state.typeSelections).length > 0) {
            return (
                Object.values(this.state.typeSelections).reduce(
                    (prev, curr) => {
                        return prev && curr
                    }
                )
            )
        }

        return false;
    };

    typesUpdate = async (event: React.ChangeEvent<{ name?: string; value: unknown; }>, port: string) => {

        await requestAPI<any>('containerizer/types', {
            body: JSON.stringify({
                port: port,
                type: event.target.value
            }),
            method: 'POST'
        });

        let currTypeSelections = this.state.typeSelections
        currTypeSelections[port] = true
        console.log('currTypeSelections: '+currTypeSelections)
        this.setState({
            typeSelections: currTypeSelections
        })
    };

    baseImageUpdate = async (value: any) => {

        await requestAPI<any>('containerizer/baseimage', {
            body: JSON.stringify({
                image: value.id
            }),
            method: 'POST'
        });
        this.setState({ baseImageSelected: true });
    };

    exctractor = async (notebookModel: INotebookModel, save = false) => {
        // try {
            const kernel = await this.getKernel()

            const extractedCell = await requestAPI<any>('containerizer/extract', {
                body: JSON.stringify({
                    save: save,
                    kernel,
                    cell_index: this.state.currentCellIndex,
                    notebook: notebookModel.toJSON()
                }),
                method: 'POST'
            });
            console.log(extractedCell);
            this.setState({ currentCell: extractedCell });
            let typeSelections: { [type: string]: boolean } = {}
    
            this.state.currentCell.inputs.forEach((el: string) => {
                typeSelections[el] = false
            })
    
            this.state.currentCell.outputs.forEach((el: string) => {
                typeSelections[el] = false
            })
    
            this.state.currentCell.params.forEach((el: string) => {
                typeSelections[el] = false
            })
            console.log('containerizer/extract typeSelections: '+typeSelections)  

            for (let key in typeSelections) {
                console.log(key + ": " + typeSelections[key]);
            }
            this.setState({ typeSelections: typeSelections })
    
            this.cellPreviewRef.current.updateChart(extractedCell['chart_obj']);
        // } catch (error) {
        //     console.log(error);
        //     alert('Error exporting cell code: ' + String(error).replace('{"message": "Unknown HTTP Error"}', ''));
        // }
    }

    onActiveCellChanged = (notebook: Notebook, _activeCell: Cell) => {
        this.setState({ currentCellIndex: notebook.activeCellIndex });
        this.exctractor(this.props.notebook.model);
    };

    handleSaveState = (_context: DocumentRegistry.Context, state: SaveState) => {
        if (state === 'completed') {
            this.exctractor(this.props.notebook.model);
        }
    };

    connectAndInitWhenReady = (notebook: NotebookPanel) => {
        notebook.context.ready.then(() => {
            this.props.notebook.content.activeCellChanged.connect(this.onActiveCellChanged);
            this.props.notebook.context.saveState.connect(this.handleSaveState);
            this.setState({ currentCellIndex: notebook.content.activeCellIndex });
        });
    };

    componentDidMount = () => {
        if (this.props.notebook) {
            this.connectAndInitWhenReady(this.props.notebook);
        }
    }

    componentDidUpdate = async (
        prevProps: Readonly<IProps>,
        _prevState: Readonly<IState>,
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

    renderDepName(dep: any): string {
        return dep['module'] + " • " + dep['name'] ? dep['module'] != "" : dep['name'];
    }

    async getKernel(){
        const sessionContext = this.props.notebook.context.sessionContext;
        const kernelObject = sessionContext?.session?.kernel; // https://jupyterlab.readthedocs.io/en/stable/api/interfaces/services.kernel.ikernelconnection-1.html#serversettings
        const kernel = (await kernelObject.info).implementation;
        return kernel
    }

    render() {
        return (
            <ThemeProvider theme={theme}>
                <div>
                    <div className={'lw-panel-editor'}>
                        <CellPreview ref={this.cellPreviewRef} />
                    </div>
                    {this.state.currentCell != null ? (
                        <div>
                            {this.state.currentCell.inputs.length > 0 ? (
                                <div>
                                    <p className={'lw-panel-preview'}>Inputs</p>
                                    <TableContainer component={Paper} className={'lw-panel-table'}>
                                        <Table aria-label="simple table">
                                            <TableBody>
                                                {this.state.currentCell.inputs.map((input: string) => (
                                                    <TableRow key={this.state.currentCell.node_id + "-" + input}>
                                                        <TableCell component="th" scope="row">
                                                            <p style={{ fontSize: "1em" }}>{input}</p>
                                                        </TableCell>
                                                        <TableCell component="th" scope="row">
                                                            <FormControl fullWidth>
                                                                <Select
                                                                    className={input}
                                                                    labelId="io-types-select-label"
                                                                    id={this.state.currentCell.node_id + "-" + input + "-select"}
                                                                    label="Type"
                                                                    onChange={(event) => { this.typesUpdate(event, input) }}
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
                                </div>
                            ) : (<div></div>)
                            }
                            {this.state.currentCell.outputs.length > 0 ? (
                                <div>
                                    <p className={'lw-panel-preview'}>Outputs</p>
                                    <TableContainer component={Paper} className={'lw-panel-table'}>
                                        <Table aria-label="simple table">
                                            <TableBody>
                                                {this.state.currentCell.outputs.map((output: string) => (
                                                    <TableRow key={this.state.currentCell.node_id + "-" + output}>
                                                        <TableCell component="th" scope="row">
                                                            <p style={{ fontSize: "1em" }}>{output}</p>
                                                        </TableCell>
                                                        <TableCell component="th" scope="row">
                                                            <FormControl fullWidth>
                                                                <Select
                                                                    labelId="io-types-select-label"
                                                                    id={this.state.currentCell.node_id + "-" + output + "-select"}
                                                                    label="Type"
                                                                    onChange={(event) => { this.typesUpdate(event, output) }}
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
                                </div>
                            ) : (<div></div>)
                            }
                            {this.state.currentCell.params.length > 0 ? (
                                <div>
                                    <p className={'lw-panel-preview'}>Parameters</p>
                                    <TableContainer component={Paper} className={'lw-panel-table'}>
                                        <Table aria-label="simple table">
                                            <TableBody>
                                                {this.state.currentCell.params.map((param: string) => (
                                                    <TableRow key={this.state.currentCell.node_id + "-" + param}>
                                                        <TableCell component="th" scope="row">
                                                            {param}
                                                        </TableCell>
                                                        <TableCell component="th" scope="row">
                                                            <FormControl fullWidth>
                                                                <Select
                                                                    labelId="param-types-select-label"
                                                                    id={this.state.currentCell.node_id + "-" + param + "-select"}
                                                                    label="Type"
                                                                    onChange={(event) => { this.typesUpdate(event, param) }}
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
                                </div>
                            ) : (<div></div>)
                            }
                            {this.state.currentCell.dependencies.length > 0 ? (
                                <div>
                                    <p className={'lw-panel-preview'}>Dependencies</p>
                                    <TableContainer component={Paper} className={'lw-panel-table'}>
                                        <Table aria-label="simple table">
                                            <TableBody>
                                                {this.state.currentCell.dependencies.map((dep: any) => (
                                                    <TableRow>
                                                        <TableCell component="th" scope="row">
                                                            {dep['module'] != '' ? (
                                                                dep['module'] + " • " + dep['name']
                                                            ) : (
                                                                dep['name']
                                                            )}
                                                        </TableCell>
                                                    </TableRow>
                                                ))}
                                            </TableBody>
                                        </Table>
                                    </TableContainer>
                                </div>
                            ) : (<div></div>)
                            }
                            <div>
                                <p className={'lw-panel-preview'}>Base Image</p>
                                <Autocomplete
                                    disablePortal
                                    onChange={(_event: any, newValue: any | null) => {
                                        this.baseImageUpdate(newValue);
                                    }}
                                    id="combo-box-demo"
                                    options={baseImages}
                                    sx={{ width: 330, margin: '20px' }}
                                    renderInput={(params) => <TextField {...params} />}
                                />
                            </div>
                        </div>
                    ) : (
                        <TableContainer></TableContainer>
                    )}
                    <div>
                        <Button variant="contained"
                            className={'lw-panel-button'}
                            onClick={this.handleCreateCell}
                            color="primary"
                            disabled={!this.allTypesSelected() || !this.state.baseImageSelected || this.state.loading}>
                            Create
                        </Button>
                    </div>
                </div>
            </ThemeProvider>
        );
    }
}