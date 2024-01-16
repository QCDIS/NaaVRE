import { styled, Tooltip } from '@material-ui/core';
import { INode, REACT_FLOW_CHART } from '@mrblenny/react-flow-chart'
import DeleteOutlinedIcon from '@mui/icons-material/DeleteOutlined';
import * as React from 'react'

const Outer = styled('div')({
  margin: '10px',
  fontSize: '14px',
  border: '1px solid lightgrey',
  borderRadius: '5px'
});

const Title = styled('span')({
  width: '100%',
  display: 'inline-block',
  height: '45px',
  borderBottom: '1px solid lightgray',
  whiteSpace: 'nowrap',
  overflow: 'hidden',
  textOverflow: 'ellipsis',
  padding: '5px',
  background: 'aliceblue'
})

const TitleSpecial = styled('span')({
  width: '100%',
  display: 'flex',
  height: '45px',
  borderBottom: '1px solid lightgray',
  justifyContent: 'center',
  alignItems: 'center',
  background: 'lavender'
})


export interface ISidebarItemProps {

  itemKey: string,
  type: string,
  ports: INode['ports'],
  properties?: any,
  itemDeleteAction?: (key: string) => void
}

export const WorkspaceItem = ({ itemKey, type, ports, properties, itemDeleteAction = null }: ISidebarItemProps) => {

  return (
    <Outer
      draggable={true}
      onDragStart={(event: any) => {
        event.dataTransfer.setData(REACT_FLOW_CHART, JSON.stringify({ type, ports, properties }))
      }}
    >
      {type != "splitter" && type != "merger" && type!= "visualizer" ? (
        <div>
          <Tooltip title={properties['title']}>
            <Title>{properties['title']}</Title>
          </Tooltip>
          <div style={{ marginTop: '5px', cursor: 'pointer' }} onClick={() => { itemDeleteAction(itemKey) }}>
            <DeleteOutlinedIcon fontSize='small' />
          </div>
        </div>
      ) : (
        <div>
          <TitleSpecial>{properties['title']}</TitleSpecial>
        </div>
      )}
    </Outer>
  )
}
