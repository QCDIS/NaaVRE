import { styled } from '@material-ui/core';
import { INode, REACT_FLOW_CHART } from '@mrblenny/react-flow-chart'
import * as React from 'react'

const Outer = styled('div')({
  padding: '15px',
  margin: '5px',
  fontSize: '14px',
  border: '1px solid lightgrey',
  borderRadius: '5px'
});

export interface ISidebarItemProps {
  type: string,
  ports: INode['ports'],
  properties?: any,
}

export const WorkspaceItem = ({ type, ports, properties }: ISidebarItemProps) => {

  return (
    <Outer
      draggable={true}
      onDragStart={(event: any) => {
        event.dataTransfer.setData(REACT_FLOW_CHART, JSON.stringify({ type, ports, properties }))
      }}
    >
      {properties['title']}
    </Outer>
  )
}
