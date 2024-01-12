import * as React from 'react';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import { green } from '@mui/material/colors';
import Button from '@mui/material/Button';
import Fab from '@mui/material/Fab';
import CheckIcon from '@mui/icons-material/Check';
import SaveIcon from '@mui/icons-material/Save';
import { requestAPI } from '@jupyter_vre/core';


interface DatasetDownloadProps {
  data: {[key: string]: any}
  query: string
}


export default function DatasetDownloadDialogue({ data, query }: DatasetDownloadProps) {
  const [loading, setLoading] = React.useState(false);
  const [success, setSuccess] = React.useState(false);
  const [downloaded_dataset_path, setDownloadedDatasetPath] = React.useState('');
  const timer = React.useRef<number>();

  const buttonSx = {
    ...(success && {
      bgcolor: green[500],
      '&:hover': {
        bgcolor: green[700],
      },
    }),
  };

  React.useEffect(() => {
    return () => {
      clearTimeout(timer.current);
    };
  }, []);


  const downloadDataset = async () => {
    try{
        const resp = await requestAPI<any>('datasetdownloadhandler', {
            body: JSON.stringify({
                docid: data['docid'],
                dataset_name: data['name']
            }),
            method: 'POST'
        });
        console.log(downloaded_dataset_path)
        console.log(resp)
        setDownloadedDatasetPath(resp['dataset_path']);
        console.log(downloaded_dataset_path)
        setSuccess(true);
        setLoading(false);
    }catch (error){
        console.log(error);
        alert(String(error).replace('{"message": "Unknown HTTP Error"}', ''));
    }
};

  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Box sx={{ m: 1, position: 'relative' }}>
        <Fab
          aria-label="save"
          color="primary"
          sx={buttonSx}
          onClick={downloadDataset}
        >
          {success ? <CheckIcon /> : <SaveIcon />}
        </Fab>
        {loading && (
          <CircularProgress
            size={68}
            sx={{
              color: green[500],
              position: 'absolute',
              top: -6,
              left: -6,
              zIndex: 1,
            }}
          />
        )}
      </Box>
      <Box sx={{ m: 1, position: 'relative' }}>
        <Button
          variant="contained"
          sx={buttonSx}
          disabled={loading}
          onClick={downloadDataset}
        >
          Download Dataset
        </Button>
        {loading && (
          <CircularProgress
            size={24}
            sx={{
              color: green[500],
              position: 'absolute',
              top: '50%',
              left: '50%',
              marginTop: '-12px',
              marginLeft: '-12px',
            }}
          />
        )}
      </Box>
    </Box>
  );
}
