import * as React from "react";
import Button from "@mui/material/Button";
import Dialog, { DialogProps } from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { Rating } from "@mui/material";
import { requestAPI } from '@jupyter_vre/core';
import ReactMarkdown from 'react-markdown'

interface NotebookDialogueProps {
  data: {[key: string]: any}
  query: string
}


export default function ScrollDialog({ data, query }: NotebookDialogueProps) {

  const [open, setOpen] = React.useState(false);
  const [rating, setRating] = React.useState(1);
  const [scroll] = React.useState<DialogProps["scroll"]>("paper");

  const handleClickOpen = (scrollType: DialogProps["scroll"]) => () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

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

  const descriptionElementRef = React.useRef<HTMLElement>(null);
  React.useEffect(() => {
    if (open) {
      const { current: descriptionElement } = descriptionElementRef;
      if (descriptionElement !== null) {
        descriptionElement.focus();
      }
    }
  }, [open]);

  return (
    <div>
      <Button onClick={handleClickOpen("paper")}>More</Button>
      <Dialog
        open={open}
        onClose={handleClose}
        scroll={scroll}
        aria-labelledby="scroll-dialog-title"
        aria-describedby="scroll-dialog-description"
      >
        <DialogTitle id="scroll-dialog-title">
          <div>
            {/* <Link href={data['html_url']}>{data['name']}</Link> */}
            <p><a href={data['html_url']} target="_blank">{data['name']}</a>.</p>
          </div>
        </DialogTitle>
        <DialogContent dividers={true}>
          <DialogContentText
            id="scroll-dialog-description"
            ref={descriptionElementRef}
            tabIndex={-1}
          >
            <ReactMarkdown>{data['description']}</ReactMarkdown>
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Rating
            name={"name"}
            defaultValue={1}
            max={5}
            onChange={(event, newValue) => {
              handleSetRating(newValue);
            }}
          />
          <Button onClick={sendRating}>Send Rating</Button>
          <Button>Download Notebook</Button>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}