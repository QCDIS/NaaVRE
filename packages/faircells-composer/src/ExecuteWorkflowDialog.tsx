import { Button, Paper, styled, Table, TableBody, TableCell, TableContainer, TableRow, TextField, ThemeProvider } from '@material-ui/core';
import * as React from 'react';
import { theme } from './Theme';
import { IChart } from '@mrblenny/react-flow-chart';
import { requestAPI } from '@jupyter_vre/core';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import { green } from '@mui/material/colors';


interface IState {
    params: []
    params_values: { [param: string]: any },
    submitted_workflow: any
}

export const DefaultState: IState = {
    params: [],
    params_values: {},
    submitted_workflow: null
}

const CatalogBody = styled('div')({
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'column',
})

interface ExecuteWorkflowDialogProps {
    chart: IChart
}

export class ExecuteWorkflowDialog extends React.Component<ExecuteWorkflowDialogProps> {

    state = DefaultState
    global_params: string[] = []

    constructor(props: ExecuteWorkflowDialogProps) {
        super(props);
        const nodes = props.chart.nodes;

        Object.keys(nodes).forEach((nid) => {
            if (nodes[nid].properties['params']) {
                this.global_params.push(...nodes[nid].properties['params']);
            }
        });
    }

    componentDidMount(): void {

        const unique_params = [...new Set(this.global_params)]
        const params_values: { [param: string]: any } = {}

        unique_params.forEach((param: string) => {
            params_values[param] = null
        });

        this.setState({
            params: unique_params,
            params_values: params_values
        });
    }

    executeWorkflow = async (values: { [param: string]: any }) => {

        const body = JSON.stringify({
            chart: this.props.chart,
            params: values
        })

        try {

            let resp = await requestAPI<any>('expmanager/execute', {
                body: body,
                method: 'POST'
            });
            this.setState({
                submitted_workflow: resp
            })
            console.log(this.state)
        } catch (error) {
            console.log(error);
            alert('Error exporting the workflow: ' + String(error).replace('{"message": "Unknown HTTP Error"}', ''));
        }

    }

    handleSubmit = () => {
        this.executeWorkflow(this.state.params_values)
    }

    handleParamValueUpdate = (event: React.ChangeEvent<{ name?: string; value: string; }>, param: string) => {
        const curr_values = this.state.params_values;
        curr_values[param] = event.target.value;
        this.setState({
            params_values: curr_values
        })
    };

    allParamsFilled = () => {

        var all_filled = true

        if (Object.values(this.state.params_values).length > 0) {

            Object.values(this.state.params_values).forEach((value) => {
                all_filled = all_filled && value != null
            });
        }

        return all_filled;
    };

    render(): React.ReactElement {
        return (
            <ThemeProvider theme={theme}>
                <p className='section-header'>Execute Workflow</p>
                <CatalogBody>
                    {this.state.submitted_workflow ? (
                        <div className='wf-submit-box'>
                            <CheckCircleOutlineIcon
                                fontSize='large'
                                sx={{ color: green[500] }}
                            />
                            <p className='wf-submit-text'>
                                Workflow submitted! You can track it <a className='wf-submit-link' target={"_blank"} href={this.state.submitted_workflow['argo_url']}>here</a>
                            </p>
                        </div>
                    ) :
                        (
                            <div>
                                <p className={'lw-panel-preview'}>Parameters</p>
                                <TableContainer component={Paper} className={'lw-panel-table'}>
                                    <Table aria-label="simple table">
                                        <TableBody>
                                            {this.state.params.map((param: string) => (
                                                <TableRow key={param}>
                                                    <TableCell component="th" scope="row">
                                                        {param}
                                                    </TableCell>
                                                    <TableCell component="th" scope="row">
                                                        <TextField
                                                            id="standard-basic"
                                                            label="Standard"
                                                            variant="standard"
                                                            onChange={(event) => { this.handleParamValueUpdate(event, param) }}
                                                        />
                                                    </TableCell>
                                                </TableRow>
                                            ))}
                                        </TableBody>
                                    </Table>
                                </TableContainer>
                                <div>
                                    <Button variant="contained"
                                        className={'lw-panel-button'}
                                        onClick={this.handleSubmit}
                                        color="primary"
                                        disabled={!this.allParamsFilled()}>
                                        Execute
                                    </Button>
                                </div>
                            </div>
                        )
                    }
                </CatalogBody>
            </ThemeProvider>
        )
    }
}