import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import datasetSearchWidget from './DatasetSearchWidget';
export default [datasetSearchWidget] as JupyterFrontEndPlugin<any>[];