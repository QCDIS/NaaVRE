import {ILayoutRestorer, JupyterFrontEnd, JupyterFrontEndPlugin} from '@jupyterlab/application';
import {
  createToolbarFactory,
  IToolbarWidgetRegistry,
  IWidgetTracker,
  ToolbarRegistry,
  WidgetTracker
} from '@jupyterlab/apputils';
import {ILauncher} from '@jupyterlab/launcher';
import {Token} from '@lumino/coreutils';
import {Widget} from '@lumino/widgets';
import {ISettingRegistry} from '@jupyterlab/settingregistry';
import {ITranslator} from '@jupyterlab/translation';
import {IObservableList} from '@jupyterlab/observables';
import {IFileBrowserFactory} from '@jupyterlab/filebrowser';

import {WorkflowModelFactory, WorkflowWidgetFactory} from './factory';
import {WorkflowWidget} from './widget';
import {ToolbarItems} from './toolbarItems';
import {Commands, CommandIDs} from './commands';

/**
 * The name of the factory that creates editor widgets.
 */
const FACTORY = 'NaaVRE workflow editor';

// Export a token so other extensions can require it
export const IWorkflowTracker = new Token<IWidgetTracker<WorkflowWidget>>(
  'naavrewfDocTracker'
);

/**
 * Initialization data for the documents extension.
 */
const extension: JupyterFrontEndPlugin<void> = {
  id: '@jupyter_vre/experiment-manager:extension',
  autoStart: true,
  requires: [
    ILayoutRestorer,
    ILauncher,
    ITranslator,
    IToolbarWidgetRegistry,
    ISettingRegistry,
    IFileBrowserFactory,
  ],
  provides: IWorkflowTracker,
  activate: (
    app: JupyterFrontEnd,
    restorer: ILayoutRestorer,
    launcher: ILauncher,
    translator: ITranslator,
    toolbarRegistry: IToolbarWidgetRegistry | null,
    settingRegistry: ISettingRegistry | null,
    browserFactory: IFileBrowserFactory,
  ) => {

    Commands.addCommands(
      app.commands,
      browserFactory,
      FACTORY,
    )

    if (launcher) {
      launcher.add({
        command: CommandIDs.createNew,
        category: 'VRE Components',
        rank: 0
      });
    }

    // Toolbar
    let toolbarFactory:
      | ((widget: Widget) => IObservableList<ToolbarRegistry.IToolbarItem>)
      | undefined;
    // Register notebook toolbar specific widgets
    if (toolbarRegistry) {
      toolbarRegistry.registerFactory<WorkflowWidget>(
        FACTORY,
        'cellsCatalog',
        widget =>
          ToolbarItems.createCellsCatalogButton(widget),
      )
      toolbarRegistry.registerFactory<WorkflowWidget>(
        FACTORY,
        'loadWorkflow',
        widget =>
          ToolbarItems.createLoadButton(widget),
      )
      toolbarRegistry.registerFactory<WorkflowWidget>(
        FACTORY,
        'saveWorkflow',
        widget =>
          ToolbarItems.createSaveButton(widget, app.commands),
      )
      toolbarRegistry.registerFactory<WorkflowWidget>(
        FACTORY,
        'exportWorkflow',
        widget =>
          ToolbarItems.createExportButton(widget),
      )
      toolbarRegistry.registerFactory<WorkflowWidget>(
        FACTORY,
        'runWorkflow',
        widget =>
          ToolbarItems.createRunButton(widget),
      )
      if (settingRegistry) {
        toolbarFactory = createToolbarFactory(
          toolbarRegistry,
          settingRegistry,
          FACTORY,
          extension.id,
          translator,
        );
      }
    }

    // Namespace for the tracker
    const namespace = 'documents-naavrewf';
    // Creating the tracker for the document
    const tracker = new WidgetTracker<WorkflowWidget>({namespace});

    // Handle state restoration.
    if (restorer) {
      // When restoring the app, if the document was open, reopen it
      restorer.restore(tracker, {
        command: 'docmanager:open',
        args: (widget) => ({path: widget.context.path, factory: FACTORY}),
        name: (widget) => widget.context.path,
      });
    }

    // register the filetype
    app.docRegistry.addFileType({
      name: 'naavrewf',
      displayName: 'NaaVRE Workflow',
      mimeTypes: ['text/json', 'application/json'],
      extensions: ['.naavrewf'],
      fileFormat: 'text',
      contentType: 'naavrewfdoc' as any,
    });

    // Creating and registering the model factory for our custom DocumentModel
    const modelFactory = new WorkflowModelFactory();
    app.docRegistry.addModelFactory(modelFactory);

    // Creating the widget factory to register it so the document manager knows about
    // our new DocumentWidget
    const widgetFactory = new WorkflowWidgetFactory({
      name: FACTORY,
      modelName: 'naavrewf-model',
      fileTypes: ['naavrewf'],
      defaultFor: ['naavrewf'],
      toolbarFactory: toolbarFactory,
    });

    // Add the widget to the tracker when it's created
    widgetFactory.widgetCreated.connect((sender, widget) => {
      // Notify the instance tracker if restore data needs to update.
      widget.context.pathChanged.connect(() => {
        tracker.save(widget);
      });
      tracker.add(widget);
    });

    // Registering the widget factory
    app.docRegistry.addWidgetFactory(widgetFactory);
  },
};

export default extension;
