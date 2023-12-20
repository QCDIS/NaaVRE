import * as React from 'react';
import {CellInfo} from "./CellInfo";
import {
  IConfig,
  IFlowChartCallbacks,
  INode,
} from "@mrblenny/react-flow-chart";
import {ChartElementEditor} from './ChartElementEditor';

interface CellEditorProps {
  callbacks: IFlowChartCallbacks,
  config: IConfig,
  node: INode,
}

export class CellEditor extends React.Component<CellEditorProps> {

  cellInfoRef: React.RefObject<CellInfo>;

  constructor(props: CellEditorProps) {
    super(props);
    this.cellInfoRef = React.createRef()
  }

  componentDidMount() {
    this.cellInfoRef.current.updateCell(
      this.props.node,
      [],
    )
  }

  render() {
    return (
      <ChartElementEditor
        title={this.props.node.properties.title}
        callbacks={this.props.callbacks}
        config={this.props.config}
      >
        <CellInfo ref={this.cellInfoRef}/>
      </ChartElementEditor>
    )
  }
}