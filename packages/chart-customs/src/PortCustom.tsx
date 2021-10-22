import styled from 'styled-components';
import { IPortDefaultProps } from '@mrblenny/react-flow-chart';
import * as React from 'react';


const PortDefaultOuter = styled.div`
  width: 25px;
  height: 25px;
  background: ${(props: { color: any; }) => props.color};
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
`

const PortSpecialOuter = styled.div`
  width: 25px;
  height: 25px;
  background: dimgray;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
`

export const PortCustom = (props: IPortDefaultProps) => {
  
  return (

    <div>
      <div>
        {props.port.properties.special_node == 1 ? 
          (<PortSpecialOuter />) :
          (<PortDefaultOuter color={props.port.properties.color} />)
        }
      </div>
    </div>
  )
}