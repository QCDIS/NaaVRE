import * as React from 'react';
import styled from 'styled-components';
import { INodeInnerDefaultProps } from "@mrblenny/react-flow-chart";


const Outer = styled.div`
  width: 200px;
  height: 100px;
  min-height: 100px;
  min-height: 70px !important;
`

export const NodeInnerCustom = ({ node, config }: INodeInnerDefaultProps) => {

    return (
        <Outer>
            <div className={'node-title-container'}>
                <p className={'node-title'}>{node.properties.title}</p>
            </div>
            {node.type == 'splitter'
            ? (<div className={'scaling-node-info'}><p>Scaling Factor: {node.properties['scalingFactor']}</p></div>) 
            : (<div></div>)}
        </Outer>
    )
}