import { requestAPI } from '@jupyter_vre/core';
import { styled, TextField } from '@material-ui/core';
import { Autocomplete } from '@mui/material';
import * as React from 'react';
import { CellInfo } from './CellInfo';
import { CellPreview } from './CellPreview';
import VirtualizedList from './VirtualizedList';

const catalogs = [

    { label: "LifeWatch ERIC" },
    { label: "BIOMAC" },
    { label: "eScience Center" }
]

interface IState {
    catalog_elements: []
}

export const DefaultState: IState = {
    catalog_elements: []
}

const CatalogBody = styled('div')({
    display: 'flex',
    flexDirection: 'row',
})

const PreviewWindow = styled('div')({
    display: 'flex',
    flexDirection: 'column'
})

export class CatalogDialog extends React.Component {

    state = DefaultState
    cellPreviewElement: React.RefObject<CellPreview>;
    cellInfoElement: React.RefObject<CellInfo>;

    constructor(props: any) {
        super(props);
        this.cellPreviewElement = React.createRef()
        this.cellInfoElement = React.createRef()
    }

    componentDidMount(): void {
        this.getCatalog()
    }

    onCellSelection = (cell_index: number) => {

        let cell = this.state.catalog_elements[cell_index];
        let chart = cell['chart_obj'];
        let node = chart['nodes'][Object.keys(chart['nodes'])[0]];
        this.cellPreviewElement.current.updateChart(chart);
        this.cellInfoElement.current.updateCell(node, cell['types']);
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
                <div>
                    <Autocomplete
                        disablePortal
                        id="combo-box-demo"
                        options={catalogs}
                        sx={{ width: 300, margin: '10px' }}
                        renderInput={(params) => <TextField {...params} label="Catalog" />}
                    />
                    <VirtualizedList
                        items={this.state.catalog_elements}
                        clickAction={this.onCellSelection}
                    />
                </div>
                <PreviewWindow>
                    <CellPreview ref={this.cellPreviewElement} />
                    <CellInfo ref={this.cellInfoElement}/>
                </PreviewWindow>
            </CatalogBody>
        )
    }
}