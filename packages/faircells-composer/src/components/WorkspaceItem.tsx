import { styled } from '@material-ui/core';
import { INode, REACT_FLOW_CHART } from '@mrblenny/react-flow-chart'
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import * as React from 'react'

const Outer = styled('div')({
  margin: '10px',
  fontSize: '14px',
  border: '1px solid lightgrey',
  borderRadius: '5px'
});

export interface ISidebarItemProps {

  itemKey           : string,
  type              : string,
  ports             : INode['ports'],
  properties?       : any,
  itemDeleteAction  : (key: string) => void
}

export const WorkspaceItem = ({ itemKey, type, ports, properties, itemDeleteAction }: ISidebarItemProps) => {

  return (
    <Outer
      draggable={true}
      onDragStart={(event: any) => {
        event.dataTransfer.setData(REACT_FLOW_CHART, JSON.stringify({ type, ports, properties }))
      }}
    >
      <p className={'workspace-item-title'}>{properties['title']}</p>
      <div style={{ marginTop: '5px', cursor: 'pointer' }} onClick={() => { itemDeleteAction(itemKey) }}>
        <DeleteOutlinedIcon fontSize='small' />
      </div>
    </Outer>
  )
}
