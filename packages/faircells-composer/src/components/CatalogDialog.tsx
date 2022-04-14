import { requestAPI } from '@jupyter_vre/core';
import { styled } from '@material-ui/core';
import * as React from 'react';
import { CellPreview } from './CellPreview';
import VirtualizedList from './VirtualizedList';

interface IState {
    catalog_elements: []
}

export const DefaultState: IState = {
    catalog_elements: []
}

const CatalogBody = styled('div')({
    minWidth: '1000px',
    minHeight: '500px',
    display: 'flex',
    flexDirection: 'row'
})

const PreviewWindow = styled('div')({
    display: 'flex',
    flexDirection: 'column'
})

const CellInfo = styled('div')({

    position: 'absolute',
    width: '100%',
    height: '230px',
    paddingTop: '20px',
    backgroundColor: 'white',
    bottom: 0
})

export class CatalogDialog extends React.Component {

    state = DefaultState
    cellPreviewElement: React.RefObject<CellPreview>;

    constructor(props: any) {
        super(props);
        this.cellPreviewElement = React.createRef()
    }

    componentDidMount(): void {
        this.getCatalog()
    }

    onCellSelection = (cell_index: number) => {

        this.cellPreviewElement.current.updateChart(this.state.catalog_elements[cell_index]['chart_obj'])
    }

    getCatalog = async () => {

        const resp = await requestAPI<any>('catalog/cells/all', {
            method: 'GET'
        });

        this.setState({ catalog_elements: resp });
    }

    render(): React.ReactElement {
        return (
            <CatalogBody>
                <VirtualizedList
                    items={this.state.catalog_elements}
                    clickAction={this.onCellSelection}
                />
                <PreviewWindow>
                    <CellPreview ref={this.cellPreviewElement} />
                    <CellInfo>
                        <div>Cell Info</div>
                    </CellInfo>
                </PreviewWindow>
            </CatalogBody>
        )
    }
}