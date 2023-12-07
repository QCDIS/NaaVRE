import * as React from 'react';
import {
	ReactWidget,
	Dialog,
	Toolbar,
	ToolbarButton,
	showDialog
	} from '@jupyterlab/apputils';
import {
	addIcon,
	codeIcon,
	fileIcon,
	runIcon,
	saveIcon,
	} from '@jupyterlab/ui-components'
import * as actions from "@mrblenny/react-flow-chart/src/container/actions";
import styled from 'styled-components'
import { theme } from './Theme';
import { mapValues } from 'lodash';
import { chartSimple } from './emptyChart';
import { FlowChart, IChart } from '@mrblenny/react-flow-chart';
import { ThemeProvider } from '@material-ui/core';
import { NodeCustom, NodeInnerCustom, PortCustom } from '@jupyter_vre/chart-customs';
import { CatalogDialog } from './CatalogDialog';
import { VRECell, requestAPI } from '@jupyter_vre/core';
import { CellEditor, Page } from '@jupyter_vre/components';
import { Workspace } from './Workspace';
import { Parallelization } from './Parallelization';
import { ExecuteWorkflowDialog } from './ExecuteWorkflowDialog';

export const CenterContent = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
`

export interface IProps { }

export interface IState {
	chart: IChart
}

export const DefaultState: IState = {
	chart: chartSimple,
}


export class Composer extends React.Component<IProps, IState> {

	state = DefaultState

	workspaceRef: React.RefObject<Workspace>;

	constructor(props: IProps) {
		super(props);
		this.workspaceRef = React.createRef();
	}

	handleAddCellToWorkspace = (cell: VRECell) => {
		this.workspaceRef.current.addElement(cell);
	}

	handleIsCellInWorkspace = (cell: VRECell) => {
		return this.workspaceRef.current.hasElement(cell);
	}

	getWorkspaceElementFromChartId = (chartId: string): VRECell => {

		let nodeId = this.state.chart.nodes[chartId].properties['og_node_id'];
		return this.workspaceRef.current.getElement(nodeId);
	}

	CatalogDialogOptions: Partial<Dialog.IOptions<any>> = {
		title: '',
		body: ReactWidget.create(
			<CatalogDialog
				addCellAction={this.handleAddCellToWorkspace}
				isCellInWorkspace={this.handleIsCellInWorkspace}
			/>
		) as Dialog.IBodyWidget<any>,
		buttons: []
	};

	ExecuteWorkflowDialogOptions: Partial<Dialog.IOptions<any>> = {
		title: '',
		body: ReactWidget.create(
			<ExecuteWorkflowDialog
				chart={this.state.chart}
			/>
		) as Dialog.IBodyWidget<any>,
		buttons: []
	};

	chartStateActions = mapValues(actions, (func: any) =>
		(...args: any) => {
			let newChartTransformer = func(...args);
			let newChart = newChartTransformer(this.state.chart);
			this.setState({
				chart: { ...this.state.chart, ...newChart }
			});
		}) as typeof actions

	loadWorkflow = async () => {
		try {
			let resp = await requestAPI<any>('expmanager/load', {
				method: 'GET'
			});
			this.setState({
				chart: resp
			})
		} catch (error) {
			console.log(error);
			alert('Error loading the workflow: ' + String(error).replace('{"message": "Unknown HTTP Error"}', ''));
		}
	}

	saveWorkflow = async () => {
		try {
			let resp = await requestAPI<any>('expmanager/save', {
				body: JSON.stringify({
					...this.state.chart
				}),
				method: 'POST'
			});
			console.log(resp);
		} catch (error) {
			console.log(error);
			alert('Error saving the workflow: ' + String(error).replace('{"message": "Unknown HTTP Error"}', ''));
		}
	}

	exportWorkflow = async () => {
		try {
			let resp = await requestAPI<any>('expmanager/export', {
				body: JSON.stringify({
					...this.state.chart
				}),
				method: 'POST'
			});
			console.log(resp);
		} catch (error) {
			console.log(error);
			alert('Error exporting the workflow: ' + String(error).replace('{"message": "Unknown HTTP Error"}', ''));
		}
	}

	getNodeEditor = () => {

		let node = this.state.chart.nodes[this.state.chart.selected.id];

		switch (node.type) {

			case "splitter":
				return (
					<div>Splitter</div>
				);

			case "merger":
				return (
					<div>Merger</div>
				);
		}

		return (
			<CellEditor cell={this.getWorkspaceElementFromChartId(this.state.chart.selected.id)} />
		);
	}

	componentDidUpdate() {

		// TODO: Implement chart sanity checks
	}

	render() {
		return (
			<ThemeProvider theme={theme} >
				<Page>
					<CenterContent>
						<FlowChart
							chart={this.state.chart}
							callbacks={this.chartStateActions}
							Components={{
								Node: NodeCustom,
								NodeInner: NodeInnerCustom,
								Port: PortCustom
							}}
						/>
						<Workspace ref={this.workspaceRef} />
						{this.state.chart.selected.id && this.state.chart.selected.type == 'node' ? (
							this.getNodeEditor()
						) :
							(<div></div>)
						}
						<Parallelization />
					</CenterContent>
				</Page>
			</ThemeProvider>
		)
	}
}

export class ComposerWidget extends ReactWidget {

	composerRef: React.RefObject<Composer>;

	constructor() {
		super();
		this.addClass('vre-composer');
		this.composerRef = React.createRef();
	}

	populateToolbar(toolbar: Toolbar) {
		toolbar.addItem('cells-catalog', new ToolbarButton({
			label: 'Cells catalog',
			tooltip: 'Open the cells catalog',
			icon: addIcon,
			onClick: () => {showDialog(this.composerRef.current.CatalogDialogOptions)},
		}))
		toolbar.addItem('load-workflow', new ToolbarButton({
			label: 'Load',
			tooltip: 'Load a workflow',
			icon: fileIcon,
			onClick: () => {this.composerRef.current.loadWorkflow()},
		}))
		toolbar.addItem('save-workflow', new ToolbarButton({
			label: 'Save',
			tooltip: 'Save the workflow',
			icon: saveIcon,
			onClick: () => {this.composerRef.current.saveWorkflow()},
		}))
		toolbar.addItem('export-workflow', new ToolbarButton({
			label: 'Export',
			tooltip: 'Export the workflow',
			icon: codeIcon,
			onClick: () => {this.composerRef.current.exportWorkflow()},
		}))
		toolbar.addItem('execute-workflow', new ToolbarButton({
			label: 'Run',
			tooltip: 'Run the workflow',
			icon: runIcon,
			onClick: () => showDialog(this.composerRef.current.ExecuteWorkflowDialogOptions),
		}))
	}

	render(): JSX.Element {
		return (
			<Composer ref={this.composerRef}/>
		);
	}
}
