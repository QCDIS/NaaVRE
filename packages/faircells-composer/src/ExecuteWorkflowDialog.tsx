import { Button, Paper, styled, Table, TableBody, TableCell, TableContainer, TableRow, TextField, ThemeProvider } from '@material-ui/core';
import * as React from 'react';
import { theme } from './Theme';
import { IChart } from '@mrblenny/react-flow-chart';


interface IState {
    params: []
    params_values: { [param: string]: any }
}

export const DefaultState: IState = {
    params: [],
    params_values: {}
}

const CatalogBody = styled('div')({
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'column',
})

interface ExecuteWorkflowDialogProps {
    chart: IChart
    executeAction: (params_values: { [param: string]: any }) => void
}

export class ExecuteWorkflowDialog extends React.Component<ExecuteWorkflowDialogProps> {

    state = DefaultState
    global_params: string[] = []

    constructor(props: ExecuteWorkflowDialogProps) {
        super(props);
        const nodes = props.chart.nodes;

        Object.keys(nodes).forEach((nid) => {
            this.global_params.push(...nodes[nid].properties['params']);
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

    handleSubmit = () => {
        this.props.executeAction(this.state.params_values)
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
                    </div>
                    <div>
                        <Button variant="contained"
                            className={'lw-panel-button'}
                            onClick={this.handleSubmit}
                            color="primary"
                            disabled={!this.allParamsFilled()}>
                            Execute
                        </Button>
                    </div>
                </CatalogBody>
            </ThemeProvider>
        )
    }
}