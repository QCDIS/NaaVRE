import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import notebookSearchWidget from './notebookSearchWidget';
export default [notebookSearchWidget] as JupyterFrontEndPlugin<any>[];
