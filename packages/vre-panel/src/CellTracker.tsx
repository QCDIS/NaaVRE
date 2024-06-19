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
import { IOutputAreaModel } from '@jupyterlab/outputarea';
import CircularProgress from '@material-ui/core/CircularProgress';
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

const DefaultState: IState = {

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
                <AddCellDialog notebook={this.props.notebook}/>
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
        await requestAPI<any>('containerizer/types', {
            body: JSON.stringify({
                port: port,
                type: event.target.value
            }),
            method: 'POST'
        });

        let currTypeSelections = this.state.typeSelections
        currTypeSelections[port] = true
        let currCurrentCell = this.state.currentCell
        currCurrentCell.types[port] = event.target.value ? String(event.target.value) : null
        this.setState({
            typeSelections: currTypeSelections,
            currentCell: currCurrentCell,
        })
    };

    baseImageUpdate = async (value: any) => {
        console.log('value: '+value);
        await requestAPI<any>('containerizer/baseimage', {
            body: JSON.stringify({
                image: value
            }),
            method: 'POST'
        });
        this.setState({ baseImageSelected: true });
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


    typeDetection = async() => {
        this.setState({loading: true});
        const panel = this.props.notebook;
    
        try {
            // Get contents of currently selected cell
            const currentCell = panel.content.activeCell;
            if (!currentCell) {
                console.log('No cell selected');
                return;
            } else if (currentCell.model.type !== 'code') {
                console.log('Selected cell is not a code cell');
                return;
            }
    
            // Clear output of currently selected cell
            const cell = panel.content.activeCell;
            const codeCell = cell as Cell & { model: { outputs: IOutputAreaModel } };
            codeCell.model.outputs.clear();
    
            // Get kernel
            const kernel = panel.sessionContext.session?.kernel;
            if (!kernel) {
                console.log('No kernel found');
                return;
            }
    
            // Get original source code
            const cellContent = currentCell.model.value.text;
    
            // Retrieve inputs, outputs, and params from extractedCell
            const extractedCell = this.state.currentCell;
            const types = extractedCell['types'];
            const inputs = extractedCell['inputs'];
            const outputs = extractedCell['outputs'];
            const params = extractedCell['params'];
    
            // Function to send code to kernel and handle response
            const sendCodeAndHandleResponse = async (code: string, vars: string[]): Promise<{ [key: string]: string }> => {
                const future = kernel.requestExecute({ code });
                let detectedTypes: { [key: string]: string } = {};
    
                return new Promise((resolve, reject) => {
                    future.onIOPub = (msg) => {
                        if (msg.header.msg_type === 'execute_result') {
                            console.log('Execution Result:', msg.content);
                        } else if (msg.header.msg_type === 'display_data') {
                            console.log('Display Data:', msg.content);
    
                            let typeString = ("data" in msg.content ? msg.content.data['text/html'] : "No data found") as string;
                            typeString = typeString.replace(/['"]/g, '');
                            const varName = vars[0];
    
                            let detectedType = null;
                            if (typeString === 'integer') {
                                detectedType = 'int';
                            } else if (typeString === 'str') {
                                detectedType = 'str';
                            } else if (typeString === 'double') {
                                detectedType = 'float';
                            } else if (typeString === 'list') {
                                detectedType = 'list';
                            } else {
                                detectedType = types[varName];
                            }
    
                            detectedTypes[varName] = detectedType;
                        
                            const output = {
                                output_type: 'display_data',
                                data: {
                                    'text/plain': vars[0] + ': ' + ("data" in msg.content ? msg.content.data['text/html'] : "No data found"),
                                },
                                metadata: {}
                            }
    
                            codeCell.model.outputs.add(output);
                            vars.shift();
                        } else if (msg.header.msg_type === 'stream') {
                            console.log('Stream:', msg);
                        } else if (msg.header.msg_type === 'error') {
                            const output = {
                                output_type: 'display_data',
                                data: {
                                    'text/plain': "evalue" in msg.content ? msg.content.evalue : "No data found",
                                },
                                metadata: {}
                            }
                            codeCell.model.outputs.add(output);
                            console.error('Error:', msg.content);
                            reject(msg.content);
                        }
                    };
    
                    future.onReply = (msg) => {
                        if (msg.content.status as string === 'aborted' || msg.content.status as string === 'ok') {
                            resolve(detectedTypes);
                        }
                    };
                });
            };

            // Create code with typeof() for inputs and params
            let inputParamSource = "";
            inputs.forEach(input => {
                inputParamSource += `\ntypeof(${input})`;
            });
            params.forEach(param => {
                inputParamSource += `\ntypeof(${param})`;
            });
            
            // Send code to check types of inputs and params
            const detectedInputParamTypes = await sendCodeAndHandleResponse(inputParamSource, [...inputs, ...params]);
            console.log('Detected Input and Param Types:', detectedInputParamTypes);
    
            // Send original source code
            await kernel.requestExecute({ code: cellContent }).done;
    
            // Create code with typeof() for outputs
            let outputSource = "";
            outputs.forEach(output => {
                outputSource += `\ntypeof(${output})`;
            });
    
            // Send code to check types of outputs
            const detectedOutputTypes = await sendCodeAndHandleResponse(outputSource, [...outputs]);
            console.log('Detected Output Types:', detectedOutputTypes);
            
            // Update the state with the detected types
            const newTypes = { ...this.state.currentCell.types, ...detectedInputParamTypes, ...detectedOutputTypes };
            const updatedCell = { ...this.state.currentCell, types: newTypes };
    
            let typeSelections: { [key: string]: boolean } = {};;
    
            updatedCell.inputs.forEach((el) => {
                typeSelections[el] = (newTypes[el] != null)
            });
    
            updatedCell.outputs.forEach((el) => {
                typeSelections[el] = (newTypes[el] != null)
            });
    
            updatedCell.params.forEach((el) => {
                typeSelections[el] = (newTypes[el] != null)
            });
    
            this.setState({
                currentCell: updatedCell,
                typeSelections: typeSelections,
            });
    
            console.log(this.state);
        } catch (error) {
            console.log(error);
        } finally {
            this.setState({loading: false});
        }
    };

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
                    <div>
                        <Button
                            variant='contained'
                            className={'lw-panel-button'}
                            onClick={this.typeDetection}
                            color='primary'
                            disabled={!this.state.currentCell || this.state.loading}
                        >
                            {this.state.loading ? (
                                <CircularProgress size={24} color="inherit" />
                            ) : (
                                'Type Detector'
                            )}
                        </Button>
                    </div>
                </div>
            </ThemeProvider>
        );
    }
}
