import {Box, Button,} from '@mui/material';
import * as React from 'react';
import {IConfig, IFlowChartCallbacks,} from "@mrblenny/react-flow-chart";

interface ChartElementEditorProps {
  children?: React.ReactNode,
  title?: string,
  callbacks: IFlowChartCallbacks,
  config: IConfig,
}

export class ChartElementEditor extends React.Component<ChartElementEditorProps> {

  constructor(props: ChartElementEditorProps) {
    super(props);
  }

  render() {
    return (
      <Box sx={{
        borderRadius: '15px',
        border: 1,
        borderColor: 'lightgrey',
        background: 'white',
        width: 380,
        transform: 'translateZ(0px)',
        flexGrow: 1,
        position: 'absolute',
        top: 20,
        right: 20
      }}>
        <p className='cell-editor section-header'>{this.props.title}</p>
        <div>
          {this.props.children}
        </div>
        <div style={{
          margin: '15px',
        }}>
          <Button
            variant="contained"
            onClick={() => {
              return this.props.callbacks.onDeleteKey({config: this.props.config})
            }
            }>Delete</Button>
        </div>
      </Box>
    )
  }
}