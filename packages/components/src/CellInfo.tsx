import { Paper, Table, TableBody, TableCell, TableContainer, TableRow } from '@material-ui/core'
import * as React from 'react'

interface IState {
    cell    : any,
    types   : []
}

export const DefaultState: IState = {
    cell    : null,
    types   : []
}

export class CellInfo extends React.Component {

    state = DefaultState;

    updateCell = (cell: any, types: []) => {

        this.setState({ cell: cell, types: types });
    }

    render() {
        return (
            <div>
                {
                    this.state.cell ? (
                        <div>
                            <p className={'lw-panel-preview'}>Inputs and Outputs</p>
                            <TableContainer component={Paper} className={'lw-panel-table'}>
                                <Table aria-label="simple table">
                                    <TableBody>
                                        {this.state.cell['properties']['vars'].map((variable: any) => (
                                            <TableRow key={variable.name}>
                                                <TableCell component="th" scope="row">
                                                    <p style={{ color: variable.color, fontSize: "1em" }}>{variable.name}</p>
                                                </TableCell>
                                                <TableCell component="th" scope="row">
                                                    {variable.direction}
                                                </TableCell>
                                                <TableCell component="th" scope="row">
                                                    {this.state.types[variable.name]}
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
                                        {this.state.cell['properties']['params'].map((param: any) => (
                                            <TableRow key={param}>
                                                <TableCell component="th" scope="row">
                                                    {param}
                                                </TableCell>
                                                <TableCell component="th" scope="row">
                                                    {this.state.types[param]}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            </TableContainer>
                        </div>
                    ) : (
                        <TableContainer></TableContainer>
                    )
                }
            </div>
        )
    }
}