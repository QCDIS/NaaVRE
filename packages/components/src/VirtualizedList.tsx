import * as React from 'react';
import { CSSProperties } from 'react';
import Box from '@mui/material/Box';
import ListItem from '@mui/material/ListItem';
import ListItemButton from '@mui/material/ListItemButton';
import ListItemText from '@mui/material/ListItemText';

function Row(
  {
    label,
    index, style, clickAction
  }: {
    label: string,
    index: number,
    style: CSSProperties,
    clickAction: (cell_index: number) => void
  }) {
  return (
    <ListItem style={style} component="div" disablePadding>
      <ListItemButton onClick={() => {
        clickAction(index);
      }}>
        <ListItemText
          primary={label}
          primaryTypographyProps={{
            style: {
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis'
            }
          }}
        />
      </ListItemButton>
    </ListItem>
  );
}

interface VirtualizedListProps {
  clickAction: (index: number) => void;
  items: [];
}

export function VirtualizedList({ items, clickAction }: VirtualizedListProps) {
  return (
    <Box
      sx={{ width: '100%', height: '100%', maxWidth: 360, bgcolor: 'background.paper', overflow: 'scroll' }}
    >
      {items.map((item, index) => (
        <Row
          key={item['node_id']}
          label={item['title']}
          index={index}
          style={{
            width: '100%',
            height: 50,
          }}
          clickAction={clickAction}
        />
      ))}
    </Box>
  );
}
