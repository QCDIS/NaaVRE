import { Link } from '@material-ui/core';
import Box from '@mui/material/Box';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';
import * as React from 'react';
import { FixedSizeList, ListChildComponentProps } from 'react-window';

function renderRow(props: ListChildComponentProps, clickAction: (cell_index: number) => void) {
  const { data, index, style } = props;

  return (
    <div>
      <ListItem style={style} key={index} component="div" disablePadding>
        <ListItemButton onClick={() => { clickAction(index) }}>
          <div>
            <ListItemText
              primary={data[index]['_source']['name']}
              style={{
                display: 'inline-block',
                maxWidth: '300px',
                whiteSpace: 'nowrap',
                overflow: 'hidden !important',
                textOverflow: 'ellipsis'
              }}
            />
            <Link
              component="div"
              style={{
                display: 'inline-block',
                maxWidth: '300px',
                whiteSpace: 'nowrap',
                overflow: 'hidden !important',
                textOverflow: 'ellipsis'
              }}>
              {data[index]['_id']}
            </Link>
          </div>
        </ListItemButton>
      </ListItem>
    </div>
  );
}

interface NotebookVirtualizedListProps {
  clickAction: (index: number) => void
  items: []
}

export default function NotebookVirtualizedList({ items, clickAction }: NotebookVirtualizedListProps) {
  return (
    <Box
      sx={{ width: '100%', height: '100%', maxWidth: 360, bgcolor: 'background.paper' }}
    >
      <FixedSizeList
        itemData={items}
        height={800}
        width={360}
        itemSize={50}
        itemCount={items.length}
        overscanCount={5}
      >
        {(props) => renderRow({ ...props }, clickAction = clickAction)}
      </FixedSizeList>
    </Box>
  );
}
