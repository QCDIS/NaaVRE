// Derived from https://github.com/jupyterlab/extension-examples/blob/2b9283f611d2471f8ac310704a3c6a896cbc1e07/documents/src/widget.tsx
// Copyright 2023 Project Jupyter Contributors; licensed under the BSD 3-Clause License license:
// https://github.com/jupyterlab/extension-examples/blob/main/LICENSE
//
// Original version has copyright 2018 Wolf Vollprecht and is licensed
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import { DocumentRegistry, DocumentWidget } from '@jupyterlab/docregistry';

import { Message } from '@lumino/messaging';

import { Signal } from '@lumino/signaling';

import { WorkflowModel } from './model';

import { ReactWidget } from '@jupyterlab/apputils';
import lodash from 'lodash';
import { Composer } from './Composer';
import React from 'react';

/**
 * DocumentWidget: widget that represents the view or editor for a file type.
 */
export class WorkflowWidget extends DocumentWidget<
  ExperimentManagerWidget,
  WorkflowModel
> {
  constructor(options: DocumentWidget.IOptions<ExperimentManagerWidget, WorkflowModel>) {
    super(options);
  }

  /**
   * Dispose of the resources held by the widget.
   */
  dispose(): void {
    this.content.dispose();
    super.dispose();
  }
}

/**
 * Widget that contains the main view of the DocumentWidget.
 */
export class ExperimentManagerWidget extends ReactWidget {

  composerRef: React.RefObject<Composer>
  private _model: WorkflowModel;

  /**
   * Construct a `ExperimentManagerWidget`.
   *
   * @param context - The document's context.
   */
  constructor(context: DocumentRegistry.IContext<WorkflowModel>) {
    super();
    this.addClass('vre-composer');
    this.composerRef = React.createRef();

    this._model = context.model;

    context.ready.then((value) => {
      this._model.contentChanged.connect(this._onContentChanged);

      this._onContentChanged();

      this.update();
    });

    this._onContentChanged();
  }

  render() {
    return (
      <Composer ref={this.composerRef}/>
    )
  }

  /**
   * Dispose of the resources held by the widget.
   */
  dispose(): void {
    if (this.isDisposed) {
      return;
    }
    this._model.contentChanged.disconnect(this._onContentChanged);
    Signal.clearData(this);
    super.dispose();
  }

  /**
   * Handle `after-attach` messages sent to the widget.
   *
   * @param msg Widget layout message
   */
  protected onAfterAttach(msg: Message): void {
    super.onAfterAttach(msg);
    this.node.addEventListener('focusout', this, true);
  }

  /**
   * Handle `before-detach` messages sent to the widget.
   *
   * @param msg Widget layout message
   */
  protected onBeforeDetach(msg: Message): void {
    this.node.removeEventListener('focusout', this, true);
    super.onBeforeDetach(msg);
  }

  /**
   * Handle event messages sent to the widget.
   *
   * @param event Event on the widget
   */
  handleEvent(event: MouseEvent): void {
    event.preventDefault();
    event.stopPropagation();

    if (event.type) {
      switch (event.type) {
        case 'focusout':
          if (! lodash.isEqual(this._model.chart, this.composerRef.current?.state.chart)) {
            this._model.chart = this.composerRef.current?.state.chart
          }
          break;
      }
    }
  }

  /**
   * Callback to listen for changes on the model. This callback listens
   * to changes on shared model's content.
   */
  private _onContentChanged = (): void => {
    this.composerRef.current?.setState({chart: this._model.chart})
  };

}
