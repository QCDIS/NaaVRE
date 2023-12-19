import Box from '@mui/material/Box';
import * as React from 'react';
import {VRECell} from '@jupyter_vre/core';
import {CellInfo} from "./CellInfo";

interface CellEditorProps {
  cell: VRECell
}

export class CellEditor extends React.Component<CellEditorProps> {

  cellInfoRef: React.RefObject<CellInfo>;

  constructor(props: CellEditorProps) {
    super(props);
    this.cellInfoRef = React.createRef()
  }

  componentDidMount() {
    this.cellInfoRef.current.updateCell(
      this.props.cell.chart_obj.nodes[this.props.cell.node_id],
      this.props.cell.types as unknown as [],
    )
  }

  render() {
    return (
      <Box sx={{
        borderRadius: '15px',
        border: 1,
        borderColor: 'lightgrey',
        boxShadow: '1px 1px lightgrey',
        background: 'white',
        zIndex: 10,
        height: 500,
        width: 500,
        transform: 'translateZ(0px)',
        flexGrow: 1,
        position: 'absolute',
        top: 20,
        right: 20
      }}>
        <p className='cell-editor section-header'>{this.props.cell.title}</p>
        <div>
          <CellInfo ref={this.cellInfoRef}/>
        </div>
      </Box>
    )
  }
}