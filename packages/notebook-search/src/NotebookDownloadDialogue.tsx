import * as React from 'react';
import Box from '@mui/material/Box';
import CircularProgress from '@mui/material/CircularProgress';
import { green } from '@mui/material/colors';
import Button from '@mui/material/Button';
import Fab from '@mui/material/Fab';
import CheckIcon from '@mui/icons-material/Check';
import SaveIcon from '@mui/icons-material/Save';
import { requestAPI } from '@jupyter_vre/core';


interface NotebookDownloadProps {
  data: {[key: string]: any}
  query: string
}


export default function NotebookDownloadDialogue({ data, query }: NotebookDownloadProps) {
  const [loading, setLoading] = React.useState(false);
  const [success, setSuccess] = React.useState(false);
  const [downloaded_notebook_path, setDownloadedNotebookPath] = React.useState('');
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


  const downloadNotebook = async () => {
    try{
        const resp = await requestAPI<any>('notebook_download', {
            body: JSON.stringify({
                docid: data['docid'],
                notebook_name: data['name']
            }),
            method: 'POST'
        });
        console.log(downloaded_notebook_path)
        console.log(resp)
        setDownloadedNotebookPath(resp['notebook_path']);
        console.log(downloaded_notebook_path)
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
          onClick={downloadNotebook}
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
          onClick={downloadNotebook}
        >
          Download Notebook
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
