import { ReactWidget, Dialog } from '@jupyterlab/apputils';
import { MessageLoop } from '@lumino/messaging';
import { Widget } from '@lumino/widgets';

export const formDialogWidget = (
  dialogComponent: JSX.Element
): Dialog.IBodyWidget<any> => {
  const widget = ReactWidget.create(dialogComponent) as Dialog.IBodyWidget<any>;
  
  MessageLoop.sendMessage(widget, Widget.Msg.UpdateRequest);

  widget.getValue = (): any => {
    const form = widget.node.querySelector('form');
    const formValues: { [key: string]: any } = {};
    for (const element of Object.values(
      form?.elements ?? []
    ) as HTMLInputElement[]) {
      switch (element.type) {
        case 'checkbox':
          formValues[element.name] = element.checked;
          break;
        default:
          formValues[element.name] = element.value;
          break;
      }
    }
    return formValues;
  };

  return widget;
};
