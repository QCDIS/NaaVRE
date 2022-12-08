import * as React from "react";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert, { AlertProps } from "@mui/material/Alert";
import { requestAPI } from '@jupyter_vre/core';


interface NotebookDownloadProps {
  data: {[key: string]: any}
  query: string
}



const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert(
  props,
  ref
) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export default function NotebookDownloadAlert({ data, query }: NotebookDownloadProps) {
  const [open, setOpen] = React.useState(false);
  const [downloaded_notebook_path, setDownloadedNotebookPath] = React.useState('');

  const downloadNotebook = async () => {
    try{
        const resp = await requestAPI<any>('notebookdownloadhandler', {
            body: JSON.stringify({
                docid: data['docid'],
                notebook_name: data['name']
            }),
            method: 'POST'
        });
        setDownloadedNotebookPath(resp['notebook_path']);
        console.log(downloaded_notebook_path)
        setOpen(true);
    }catch (error){
        console.log(error);
        alert(String(error).replace('{"message": "Unknown HTTP Error"}', ''));
    }
};

  const handleClose = (
    event?: React.SyntheticEvent | Event,
    reason?: string
  ) => {
    if (reason === "clickaway") {
      return;
    }

    setOpen(false);
  };

  return (
    <Stack spacing={2} sx={{ width: "100%" }}>
      <p> </p>
      <p> </p>
      <Button variant="contained" 
        onClick={downloadNotebook}
        >
        Download Notebook
      </Button>
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity="success" sx={{ width: "100%" }}>
          Download Copleted. The notebook is at {downloaded_notebook_path}
        </Alert>
      </Snackbar>
    </Stack>
  );
}