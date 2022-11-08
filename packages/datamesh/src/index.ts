import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import datameshWidget from './datameshWidget';
export default [datameshWidget] as JupyterFrontEndPlugin<any>[];
