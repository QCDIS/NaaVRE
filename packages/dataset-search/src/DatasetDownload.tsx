import * as React from "react";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert, { AlertProps } from "@mui/material/Alert";
import { requestAPI } from '@jupyter_vre/core';


interface DatasetDownloadProps {
  data: {[key: string]: any}
}



const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert(
  props,
  ref
) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export default function DatasetDownloadAlert({ data }: DatasetDownloadProps) {
  const [open, setOpen] = React.useState(false);
  const [downloaded_dataset_path, setDownloadedDatasetPath] = React.useState('');

  const downloadDataset = async () => {
    try{
        const resp = await requestAPI<any>('datasetdownloadhandler', {
            body: JSON.stringify({
                uuid: data['uuid'],
                title: data['title']
            }),
            method: 'POST'
        });
        setDownloadedDatasetPath(resp['dataset_path']);
        console.log(downloaded_dataset_path)
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
      <Button 
        sx={{ width: 150, padding: 1, margin: 2 }} 
        variant="contained" 
        onClick={downloadDataset}
        >
        Download Dataset
      </Button>
      <Snackbar open={open} autoHideDuration={2000} onClose={handleClose}>
        <Alert onClose={handleClose} severity="success" sx={{ width: "25%" }}>
          Download Copleted. The dataset is at {downloaded_dataset_path}
        </Alert>
      </Snackbar>
    </Stack>
  );
}