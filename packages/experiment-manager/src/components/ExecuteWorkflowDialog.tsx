import {Button, styled, ThemeProvider} from '@material-ui/core';
import * as React from 'react';
import {theme} from './Theme';
import {IChart} from '@mrblenny/react-flow-chart';
import {requestAPI, VRECell} from '@jupyter_vre/core';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import AutoModeIcon from '@mui/icons-material/AutoMode';
import {grey, green} from '@mui/material/colors';
import TableContainer from "@mui/material/TableContainer";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import TextField from '@mui/material/TextField';

interface IState {
  params: string[]
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
  overflow: 'scroll',
  flexDirection: 'column',
})

interface ExecuteWorkflowDialogProps {
  chart: IChart
}

export class ExecuteWorkflowDialog extends React.Component<ExecuteWorkflowDialogProps> {

  state = DefaultState
  global_params: string[] = []
  chart_node_ids: string[] = []

  constructor(props: ExecuteWorkflowDialogProps) {
    super(props);
    const nodes = props.chart.nodes;

    Object.keys(nodes).forEach((nid) => {
      if (nodes[nid].properties['params']) {
        this.global_params.push(...nodes[nid].properties['params']);
        this.chart_node_ids.push(nodes[nid].properties['og_node_id']);
      }
    });

    const unique_params = [...new Set(this.global_params)].sort()
    const params_values: { [param: string]: any } = {}

    unique_params.forEach((param: string) => {
      params_values[param] = null
    });

    this.state.params = unique_params
    this.state.params_values = params_values

  }

  getValuesFromCatalog = async () => {
    const catalog = await requestAPI<any>('catalog/cells/all', {
      method: 'GET'
    });
    const params_values = this.state.params_values
    // Extract param values for cells that are in the current workflow
    catalog.forEach((catalogItem: VRECell) => {
      if (this.chart_node_ids.includes(catalogItem.node_id)) {
        Object.keys(catalogItem.param_values).forEach((paramName) => {
          params_values[paramName] = catalogItem.param_values[paramName]
        })
      }
    })
    this.setState({
      params_values: params_values,
    })
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
                  sx={{color: green[500]}}
                />
                <p className='wf-submit-text'>
                  Workflow submitted! You can track it <a className='wf-submit-link' target={"_blank"}
                                                          href={this.state.submitted_workflow['argo_url']}>here</a>
                </p>
              </div>
            ) :
            (
              <div>
                <div style={{
                  textAlign: 'right',
                  padding: '10px 15px 0 0',
                }}
                >
                  <Button
                    disabled={false}
                    onClick={this.getValuesFromCatalog}
                    size="small"
                    variant="text"
                    endIcon={<AutoModeIcon fontSize="inherit" />}
                    style={{color: grey[900], textTransform: 'none'}}
                  >
                    Use notebook values
                  </Button>
                </div>
                <TableContainer >
                  <Table stickyHeader aria-label="sticky table">
                    <TableBody>
                      {this.state.params.map((param: string) => (
                        <TableRow hover role="checkbox" tabIndex={-1} key={param}>
                          <TableCell key={param} align={"right"}>
                            {param}
                          </TableCell>
                          <TableCell component="th" scope="row">
                            <TextField
                              // id="standard-basic"
                              // label="Standard"
                              // variant="standard"
                              value={this.state.params_values[param]}
                              onChange={(event) => {
                                this.handleParamValueUpdate(event, param)
                              }}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                <Button variant="contained"
                        className={'lw-panel-button'}
                        onClick={this.handleSubmit}
                        color="primary"
                        disabled={!this.allParamsFilled()}>
                  Execute
                </Button>
              </div>
            )
          }
        </CatalogBody>
      </ThemeProvider>
    )
  }
}