import * as React from 'react';
import styled from 'styled-components';
import { INodeInnerDefaultProps } from "@mrblenny/react-flow-chart";


const NodeInnerContainer = styled.div`
    min-height: 100px;
`

export const NodeInnerCustom = ({ node, config }: INodeInnerDefaultProps) => {

    return (
        <NodeInnerContainer>
        </NodeInnerContainer>
    )
}