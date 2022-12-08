import * as React from "react";
import Button from "@mui/material/Button";
import Dialog, { DialogProps } from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import ReactMarkdown from 'react-markdown'
import NotebookDownload from "./NotebookDownload"
import NotebookSendRating from "./NotebookSendRating"



interface NotebookDialogueProps {
  data: {[key: string]: any}
  query: string
}


export default function NotebookScrollDialog({ data, query }: NotebookDialogueProps) {

  const [open, setOpen] = React.useState(false);
  const [scroll] = React.useState<DialogProps["scroll"]>("paper");

  const handleClickOpen = (scrollType: DialogProps["scroll"]) => () => {
    setOpen(true);
    
  };

  const handleClose = () => {
    setOpen(false);
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
      <Button variant="contained" onClick={handleClickOpen("paper")}>More</Button>
      <Dialog
        open={open}
        onClose={handleClose}
        scroll={scroll}
        aria-labelledby="scroll-dialog-title"
        aria-describedby="scroll-dialog-description"
      >
        <DialogTitle id="scroll-dialog-title">
          <p>{data['name']}.</p>
          <div className={'nb-download-link'}>
            <p><a href={data['html_url']} target="_blank">{data['html_url']}</a>.</p>
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
          <NotebookSendRating
              data = {data}
              query= {query}/>

          <NotebookDownload
              data = {data}
              query= {query}/>
          <p> </p>
          <p> </p>
          <p> </p>
          <p> </p>
          <Button variant="contained" onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}