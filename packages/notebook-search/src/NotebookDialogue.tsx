import * as React from "react";
import Button from "@mui/material/Button";
import Dialog, { DialogProps } from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
import { Rating } from "@mui/material";

export default function ScrollDialog(data: any) {
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
    try {
      console.log("resp: ", rating);
    } catch (error) {
      console.log(error);
      alert(String(error).replace('{"message": "Unknown HTTP Error"}', ""));
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
        <DialogTitle id="scroll-dialog-title">{data['name']}</DialogTitle>
        <DialogContent dividers={true}>
          <DialogContentText
            id="scroll-dialog-description"
            ref={descriptionElementRef}
            tabIndex={-1}
          >
            <MuiMarkdown>{data['description']}</MuiMarkdown>;
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
          <Button onClick={sendRating}>Send Rating </Button>
          <Button>Download Notebook</Button>
          <Button onClick={handleClose}>Close</Button>
        </DialogActions>
      </Dialog>
    </div>
  );
}