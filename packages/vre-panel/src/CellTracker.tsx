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
import { Autocomplete, LinearProgress, Alert, Box } from '@mui/material';
import { AddCellDialog } from './AddCellDialog';

interface IProps {
    notebook: NotebookPanel;
}

interface IState {
    loading: boolean
    extractorError: string,
    baseImageSelected: boolean
    currentCellIndex: number
    currentCell: VRECell
    typeSelections: { [type: string]: boolean }
    baseImages: any[]
}

export const DefaultState: IState = {
    loading: false,
    extractorError: '',
    baseImageSelected: false,
    currentCellIndex: -1,
    currentCell: null,
    typeSelections: {},
    baseImages: []
}

type SaveState = 'started' | 'completed' | 'failed';
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
                <AddCellDialog notebook={this.props.notebook} cell={this.state.currentCell}/>
            ) as Dialog.IBodyWidget<any>,
            buttons: []
        };
        showDialog(AddCellDialogOptions)
    }

    allTypesSelected = () => {
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

    getVarType(var_name: string): string | null {
        return (var_name in this.state.currentCell.types) && this.state.currentCell.types[var_name];
    }

    async loadBaseImages() {
        try {
            const baseImagesData = await requestAPI<any>(
              'containerizer/baseimagetags',
              { method: 'GET' }
            )

            // Convert object data to an array of objects
            const updatedBaseImages = Object.entries(baseImagesData).map(
              ([name, image]) => ({ name, image})
            )
            console.log('updatedBaseImages');
            console.log(updatedBaseImages);
            this.setState({baseImages: updatedBaseImages });
        } catch (error) {
            console.log(error);
        }
    }


    typesUpdate = async (event: React.ChangeEvent<{ name?: string; value: unknown; }>, port: string) => {
        // await requestAPI<any>('containerizer/types', {
        //     body: JSON.stringify({
        //         port: port,
        //         type: event.target.value
        //     }),
        //     method: 'POST'
        // });

        let currTypeSelections = this.state.typeSelections
        currTypeSelections[port] = true
        let currCurrentCell = this.state.currentCell
        currCurrentCell.types[port] = event.target.value ? String(event.target.value) : null
        this.setState({
            typeSelections: currTypeSelections,
            currentCell: currCurrentCell,
        })
        console.log(`currentCell: ${JSON.stringify(this.state.currentCell)}`)
    };

    baseImageUpdate = async (value: any) => {
        console.log('value: '+value);
        // await requestAPI<any>('containerizer/baseimage', {
        //     body: JSON.stringify({
        //         image: value
        //     }),
        //     method: 'POST'
        // });
        this.state.currentCell.base_image = value
        this.setState({ baseImageSelected: true });
        console.log(`currentCell: ${JSON.stringify(this.state.currentCell)}`)
    };

    extractor = async (notebookModel: INotebookModel, save = false) => {
        await this.loadBaseImages();
        const kernel = await this.getKernel()
        try {
            this.setState({
                loading: true,
                extractorError: '',
            })

            const extractedCell = await requestAPI<any>('containerizer/extract', {
                body: JSON.stringify({
                    save: save,
                    kernel,
                    cell_index: this.state.currentCellIndex,
                    notebook: notebookModel.toJSON()
                }),
                method: 'POST'
            });
            console.log(`Extracted cell: ${JSON.stringify(extractedCell)}`);
            this.setState({
                currentCell: extractedCell,
                loading: false,
                extractorError: '',
            });
            let typeSelections: { [type: string]: boolean } = {}

            this.state.currentCell.inputs.forEach((el: string) => {
                typeSelections[el] = (this.getVarType(el) != null)
            })

            this.state.currentCell.outputs.forEach((el: string) => {
                typeSelections[el] = (this.getVarType(el) != null)
            })

            this.state.currentCell.params.forEach((el: string) => {
                typeSelections[el] = (this.getVarType(el) != null)
            })
            this.setState({ typeSelections: typeSelections })

            this.cellPreviewRef.current.updateChart(extractedCell['chart_obj']);
        } catch (error) {
            console.log(error);
            this.setState({
                loading: false,
                extractorError: String(error),
            })
        }
    }

    onActiveCellChanged = (notebook: Notebook, _activeCell: Cell) => {
        this.setState({ currentCellIndex: notebook.activeCellIndex });
        this.extractor(this.props.notebook.model);
    };

    handleSaveState = (_context: DocumentRegistry.Context, state: SaveState) => {
        if (state === 'completed') {
            this.extractor(this.props.notebook.model);
        }
    };

    connectAndInitWhenReady = (notebook: NotebookPanel) => {
        notebook.context.ready.then(() => {
            this.props.notebook.content.activeCellChanged.connect(this.onActiveCellChanged);
            this.props.notebook.context.saveState.connect(this.handleSaveState);
            this.setState({ currentCellIndex: notebook.content.activeCellIndex });
        });
    };

    async componentDidMount() {
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
                    {this.state.extractorError && (
                      <div>
                          <Alert severity="error" className={'lw-panel-preview'}>
                              <p>Notebook cannot be analyzed: {this.state.extractorError}</p>
                          </Alert>
                      </div>
                    )}
                    {(this.state.currentCell != null && !this.state.loading) ? (
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
                                                                    labelId="io-types-select-label"
                                                                    id={this.state.currentCell.node_id + "-" + input + "-select"}
                                                                    label="Type"
                                                                    value={this.getVarType(input)}
                                                                    error={this.getVarType(input) == null}
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
                                                                    value={this.getVarType(output)}
                                                                    error={this.getVarType(output) == null}
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
                                                                    value={this.getVarType(param)}
                                                                    error={this.getVarType(param) == null}
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
                                    getOptionLabel={(option) => option.name}
                                    options={this.state.baseImages}
                                    disablePortal
                                    onChange={(_event: any, newValue: any | null) => {
                                        this.baseImageUpdate(newValue.image);
                                    }}
                                    id="combo-box-demo"
                                    sx={{ width: 330, margin: '20px' }}
                                    renderInput={(params) => <TextField {...params} />}
                                />
                            </div>
                        </div>
                    ) : (
                        <div>
                            {this.state.loading ? (
                                <div>
                                    <p className={'lw-panel-preview'}>
                                        <span>Analyzing notebook</span>
                                        <br/>
                                        <span style={{color: '#aaaaaa'}}>This can take up to a minute</span>
                                    </p>
                                    <Box className={'lw-panel-table'} sx={{width: '100%'}}>
                                        <LinearProgress/>
                                    </Box>
                                </div>
                            ) : (
                                <TableContainer>
                                </TableContainer>
                            )}
                        </div>
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