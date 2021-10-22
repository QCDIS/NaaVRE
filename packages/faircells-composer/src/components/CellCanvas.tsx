import { cloneDeep, mapValues } from 'lodash'
import * as React from 'react'
import { FlowChart } from '@mrblenny/react-flow-chart'
import * as actions from '@mrblenny/react-flow-chart/src/container/actions'
import { Page } from '.'
import { chartSimple } from '../exampleChart'

export class CellCanvas extends React.Component {
    public state = cloneDeep(chartSimple)
    public render () {
      const chart = this.state
      const stateActions = mapValues(actions, (func: any) =>
        (...args: any) => this.setState(func(...args))) as typeof actions
  
      return (
        <Page>
          <FlowChart
            chart={chart}
            callbacks={stateActions}
          />
        </Page>
      )
    }
  }