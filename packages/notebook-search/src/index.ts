import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import notebookSearchWidget from './NotebookSearchWidget';
export default [notebookSearchWidget] as JupyterFrontEndPlugin<any>[];
