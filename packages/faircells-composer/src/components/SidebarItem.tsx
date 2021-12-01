import { INode, REACT_FLOW_CHART } from '@mrblenny/react-flow-chart'
import { Dialog, showDialog } from '@jupyterlab/apputils';
import * as React from 'react'
import styled from 'styled-components'
import { requestAPI } from '@jupyter_vre/core';

const Outer = styled.div`
  padding: 15px;
  margin: 5px;
  font-size: 14px;
  background: lightblue;
  border: 1px solid lightgrey;
  border-radius: 5px;
  cursor: move;
`

export interface ISidebarItemProps {
  type: string,
  ports: INode['ports'],
  properties?: any,
}

export const SidebarItem = ({ type, ports, properties }: ISidebarItemProps) => {

  function click() {
    showDialog({
      title: 'Delete',
      body: (
        <p>Confirm Deletion of '{properties['title']}' ?</p>
      ),
      buttons: [Dialog.okButton(), Dialog.cancelButton()]
    }).then((res) => {

        if (res.button.label == 'OK') {

          requestAPI<any>('catalog/cells', {
            body: JSON.stringify(properties),
            method: 'DELETE'
          }).then((resp) => {
            console.log(resp);
          });
        }
    });
  }

  return (
    <Outer
      clickable={false}
      onClick={click}
      draggable={true}
      onDragStart={(event: any) => {
        event.dataTransfer.setData(REACT_FLOW_CHART, JSON.stringify({ type, ports, properties }))
      }}
    >
      {properties['title']}
    </Outer>
  )
}
