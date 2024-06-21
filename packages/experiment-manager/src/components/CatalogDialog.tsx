import { requestAPI, VRECell, CellPreview  } from '@jupyter_vre/core';
import { Button, styled, TextField, ThemeProvider } from '@material-ui/core';
import { Autocomplete } from '@mui/material';
import * as React from 'react';
import { VirtualizedList, CellInfo } from '@jupyter_vre/components';
import { theme } from './Theme';

const catalogs = [

    { label: "Local" }
]

interface IState {
    catalog_elements: []
    current_cell: VRECell
    current_cell_in_workspace: boolean
}

export const DefaultState: IState = {
    catalog_elements: [],
    current_cell: null,
    current_cell_in_workspace: false
}

const CatalogBody = styled('div')({
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'row',
})

const PreviewWindow = styled('div')({
    width: '400px',
    display: 'flex',
    flexDirection: 'column',
    overflowY: 'scroll'
})

interface CatalogDialogProps {
    addCellAction: (cell: VRECell) => void
    isCellInWorkspace: (cell: VRECell) => boolean
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
        let chart = cell['chart_obj'];
        let node = chart['nodes'][Object.keys(chart['nodes'])[0]];
        this.cellPreviewRef.current.updateChart(chart);
        this.cellInfoRef.current.updateCell(node, cell['types']);

        this.setState({
            current_cell: cell,
            current_cell_in_workspace: this.props.isCellInWorkspace(cell)
        });
    }

    onCellAddition = () => {

        this.props.addCellAction(this.state.current_cell);
        this.setState({ current_cell_in_workspace: true })
    }

    getCatalog = async () => {

        const resp = await requestAPI<any>('catalog/cells/all', {
            method: 'GET'
        });
        console.log(`Cells: ${JSON.stringify(resp)}`)
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
                        <div>
                            <CellPreview ref={this.cellPreviewRef} />
                            <CellInfo ref={this.cellInfoRef} />
                            {this.state.current_cell != null ? (
                                <Button color="primary"
                                    disabled={this.state.current_cell_in_workspace}
                                    style={{ margin: '15px' }}
                                    variant="contained"
                                    onClick={this.onCellAddition}>
                                    Add to Workspace
                                </Button>
                            ) : (<div></div>)}
                        </div>
                    </PreviewWindow>
                </CatalogBody>
            </ThemeProvider>
        )
    }
}