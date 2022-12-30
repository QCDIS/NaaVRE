import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import lifewatchVREPlugin from './NotebookContainerizer2widget';
export default [lifewatchVREPlugin] as JupyterFrontEndPlugin<any>[];