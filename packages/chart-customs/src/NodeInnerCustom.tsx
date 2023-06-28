import * as React from 'react';
import styled from 'styled-components';
import CallSplitIcon from '@mui/icons-material/CallSplit';
import CallMergeIcon from '@mui/icons-material/CallMerge';
import ImageIcon from '@mui/icons-material/Image';
import { INodeInnerDefaultProps } from "@mrblenny/react-flow-chart";


const NodeInnerContainer = styled.div`
    min-height: 100px;
`

const SpecialIconContainer = styled.div`
    padding: 5px;
    display: flex;
    justify-content: center;
`

export const NodeInnerCustom = ({ node, config }: INodeInnerDefaultProps) => {

    const getSpecialIcon = (nodeType: string) => {

        if (nodeType == "splitter") {
            return (
                <CallSplitIcon sx={{fontSize: '50px', transform: 'rotate(90deg)'}}/>
            )
        }

        if (nodeType == "merger") {
            return (
                <CallMergeIcon sx={{fontSize: '50px', transform: 'rotate(90deg)'}}/>
            )
        }
        
        if (nodeType == "visualizer") {
            return (
                <ImageIcon sx={{fontSize: '50px'}}/>
            )
        }
    }

    return (
        <NodeInnerContainer>
            {node.type == "splitter" || node.type == "merger" || node.type == "visualizer" ? (
            <SpecialIconContainer>
                {getSpecialIcon(node.type)}
                </SpecialIconContainer>
            ) : (
                <div></div>
            )}
        </NodeInnerContainer>
    )
}
