import { requestAPI } from '@jupyter_vre/core';
import { Avatar, styled, TextField } from '@material-ui/core';
import { Autocomplete } from '@mui/material';
import * as React from 'react';
import DownloadForOffline from '@mui/icons-material/DownloadForOffline';
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

const CellInfo = styled('div')({

    position: 'absolute',
    display: 'flex',
    flexDirection: 'column',
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
                    <CellInfo>
                        <div style={{ display: 'flex', flexDirection: 'row' }}>
                            <Avatar>NS</Avatar>
                            <p style={{ padding: '15px' }}>Name Surname</p>
                            <DownloadForOffline sx={{ margin: '10px' }} fontSize='medium' />
                        </div>
                        <div style={{ marginTop: '20px', textAlign: 'justify', width: '500px' }}>
                            Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque dignissim tortor id neque egestas blandit. In hac habitasse platea dictumst. Nam feugiat blandit enim at pharetra. Duis rhoncus urna erat, quis posuere lorem consectetur non. Proin imperdiet lectus id nulla semper sagittis. Etiam ut leo sit amet lacus malesuada dignissim. Aenean ut turpis felis. Donec molestie, libero vitae imperdiet dictum, metus libero ullamcorper turpis, ut euismod mauris nulla a dui. Maecenas efficitur tristique posuere. Sed porta convallis elit, vel pulvinar dolor pulvinar vel. In scelerisque velit in dictum dictum. Praesent eget lacus sapien.
                        </div>
                    </CellInfo>
                </PreviewWindow>
            </CatalogBody>
        )
    }
}