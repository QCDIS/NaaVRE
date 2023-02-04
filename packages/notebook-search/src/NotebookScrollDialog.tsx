import * as React from "react";
import Button from "@mui/material/Button";
import Dialog, { DialogProps } from "@mui/material/Dialog";
import DialogActions from "@mui/material/DialogActions";
import DialogContent from "@mui/material/DialogContent";
import DialogContentText from "@mui/material/DialogContentText";
import DialogTitle from "@mui/material/DialogTitle";
// import ReactMarkdown from 'react-markdown'
import NotebookDownload from "./NotebookDownload"
import NotebookSendRating from "./NotebookSendRating"
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import { requestAPI } from '@jupyter_vre/core';
import { IpynbRenderer } from "react-ipynb-renderer";
import { ThemeProvider } from '@material-ui/core';
import { theme } from './Theme';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

interface NotebookDialogueProps {
  data: {[key: string]: any}
  query: string
}


function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

export default function NotebookScrollDialog({ data, query }: NotebookDialogueProps) {
  const [value, setValue] = React.useState(0);
  const [notebook_source_file, setNotebookSourceFile] = React.useState( { cells: [] } );


  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  


  const [open, setOpen] = React.useState(false);
  const [scroll] = React.useState<DialogProps["scroll"]>("paper");


  const getNotebookSource = async () => {
    try{
        const resp = await requestAPI<any>('notebook_source', {
            body: JSON.stringify({
                docid: data['docid'],
                notebook_name: data['name']
            }),
            method: 'POST'
        });
        setNotebookSourceFile(resp['notebook_source']);
        setOpen(true);
    }catch (error){
        console.log(error);
        alert(String(error).replace('{"message": "Unknown HTTP Error"}', ''));
    }
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
    <ThemeProvider theme={theme}>
    <div>
      <Button 
      variant="contained" 
      onClick={ getNotebookSource }
      >
        More
      </Button>
      <Dialog
        fullScreen
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
            <Box sx={{ width: '100%' }}>
            <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
              <Tabs value={value} onChange={handleChange} aria-label="basic tabs example">
                <Tab label="Notebook" {...a11yProps(0)} />
                {/* <Tab label="Description" {...a11yProps(1)} /> */}
              </Tabs>
            </Box>
            <TabPanel value={value} index={0}>
              <IpynbRenderer 
                  ipynb={notebook_source_file}/>
            </TabPanel>
          </Box>

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
          <Button 
            sx={{ width: 150, padding: 1, margin: 2 }} 
            variant="contained" onClick={handleClose}>
              Close
          </Button>
        </DialogActions>
      </Dialog>
    </div>
    </ThemeProvider>
  );
}