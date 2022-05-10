import { requestAPI } from '@jupyter_vre/core';
import { Button, styled, TextField, ThemeProvider } from '@material-ui/core';
import { Autocomplete } from '@mui/material';
import * as React from 'react';
import { CellInfo } from './CellInfo';
import { CellPreview } from './CellPreview';
import VirtualizedList from './CatalogVirtualizedList';
import { FairCell } from '../faircell';
import { theme } from '../Theme';

const catalogs = [

    { label: "LifeWatch ERIC" },
    { label: "BIOMAC" },
    { label: "eScience Center" }
]

interface IState {
    catalog_elements: []
    current_cell: FairCell
}

export const DefaultState: IState = {
    catalog_elements: [],
    current_cell: null
}

const CatalogBody = styled('div')({
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'row',
})

const PreviewWindow = styled('div')({
    display: 'flex',
    flexDirection: 'column',
    overflowY: 'scroll'
})

interface CatalogDialogProps {
    addCellAction: (cell: FairCell) => void
}

export class CatalogDialog extends React.Component<CatalogDialogProps> {

    state = DefaultState
    cellPreviewRef: React.RefObject<CellPreview>;
    cellInfoRef: React.RefObject<CellInfo>;

    constructor(props: CatalogDialogProps) {
        super(props);
        this.cellPreviewRef = React.createRef()
        this.cellInfoRef = React.createRef()
    }

    componentDidMount(): void {
        this.getCatalog()
    }

    onCellSelection = (cell_index: number) => {

        let cell = this.state.catalog_elements[cell_index];
        this.setState({ current_cell: cell });
        let chart = cell['chart_obj'];
        let node = chart['nodes'][Object.keys(chart['nodes'])[0]];
        this.cellPreviewRef.current.updateChart(chart);
        this.cellInfoRef.current.updateCell(node, cell['types']);
    }

    getCatalog = async () => {

        const resp = await requestAPI<any>('catalog/cells/all', {
            method: 'GET'
        });

        this.setState({ catalog_elements: resp });
    }

    render(): React.ReactElement {
        return (
            <ThemeProvider theme={theme}>
                <p className='section-header'>Explore Cell Catalogs</p>
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
                        <CellPreview ref={this.cellPreviewRef} />
                        <CellInfo ref={this.cellInfoRef} />
                        <Button color="primary"
                            style={{ margin: '15px' }}
                            variant="contained"
                            onClick={() => { this.props.addCellAction(this.state.current_cell) }}>
                            Add to Workspace
                        </Button>
                    </PreviewWindow>
                </CatalogBody>
            </ThemeProvider>
        )
    }
}