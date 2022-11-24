import * as React from "react";
import Stack from "@mui/material/Stack";
import Button from "@mui/material/Button";
import Snackbar from "@mui/material/Snackbar";
import MuiAlert, { AlertProps } from "@mui/material/Alert";
import { requestAPI } from '@jupyter_vre/core';
import { Rating } from "@mui/material";


interface NotebookSendRatingAlertProps {
  data: {[key: string]: any}
  query: string
}



const Alert = React.forwardRef<HTMLDivElement, AlertProps>(function Alert(
  props,
  ref
) {
  return <MuiAlert elevation={6} ref={ref} variant="filled" {...props} />;
});

export default function NotebookSendRatingAlert({ data, query }: NotebookSendRatingAlertProps) {
  const [open, setOpen] = React.useState(false);
  const [rating, setRating] = React.useState(1);


  const handleSetRating = (starRating: number) => {
    setRating(starRating);
  };


  const sendRating = async () => {
    try{
        console.log('query: ',query)
        console.log('rating: ',rating)
        console.log('notebook: ',data)
        const resp = await requestAPI<any>('notebooksearchrating', {
            body: JSON.stringify({
                keyword: query,
                notebook: data,
                rating: rating
            }),
            method: 'POST'
        });
        console.log(resp)
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
      <Rating
            name={"name"}
            defaultValue={1}
            max={5}
            onChange={(event, newValue) => {
              handleSetRating(newValue);
            }}
          />
      <Button variant="contained" onClick={sendRating}>
      Send Rating
      </Button>
      <Snackbar open={open} autoHideDuration={6000} onClose={handleClose}>
        <Alert onClose={handleClose} severity="success" sx={{ width: "100%" }}>
          Rating sent!
        </Alert>
      </Snackbar>
    </Stack>
  );
}