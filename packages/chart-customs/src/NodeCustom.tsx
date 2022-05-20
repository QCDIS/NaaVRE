import { INodeDefaultProps } from '@mrblenny/react-flow-chart';
import styled from 'styled-components';
import * as React from 'react';

const NodeContainer = styled.div`
    position: absolute;
    background: white;
    width: 250px;
    height: 150px;
    border-radius: 5px;
    border: 1px solid lightgray;
`
const NodeContainerSpecial = styled.div`
    position: absolute;
    background: white;
    width: 200px;
    height: 100px;
    border-radius: 5px;
    border: 1px solid lightgray;
`

const NodeChildrenContainer = styled.div``

const NodeTitleContainer = styled.div`
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    padding: 5px;
    background-color: aliceblue;
    text-align: center;
`

const NodeTitleContainerSpecial = styled.div`
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    padding: 5px;
    background-color: lavender;
    text-align: center;
`

const NodeTitle = styled.span`
    font-size: small;
    display: inline-block;
    max-width: 200px;
    white-space: nowrap;
    overflow: hidden !important;
    text-overflow: ellipsis;
`

const renderNode = ({ node, children, ...otherProps }: INodeDefaultProps, ref: React.ForwardedRef<HTMLDivElement>) => {

    if (node.type == "splitter" || node.type == "merger") {
        return (
            <NodeContainerSpecial ref={ref} {...otherProps}>
                <NodeTitleContainerSpecial>
                    <NodeTitle>{node.properties.title}</NodeTitle>
                </NodeTitleContainerSpecial>
                <NodeChildrenContainer>
                    {children}
                </NodeChildrenContainer>
            </NodeContainerSpecial>
        )
    }

    return (
        <NodeContainer ref={ref} {...otherProps} >
            <NodeTitleContainer>
                <NodeTitle>{node.properties.title}</NodeTitle>
            </NodeTitleContainer>
            <NodeChildrenContainer>
                {children}
            </NodeChildrenContainer>
        </NodeContainer >
    )
}

const NodeCustomRender: React.ForwardRefRenderFunction<HTMLDivElement, INodeDefaultProps> = ({ node, children, ...otherProps }, ref) => {

    return renderNode({ node, children, ...otherProps }, ref)
}

export const NodeCustom = React.forwardRef(NodeCustomRender);

