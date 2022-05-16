import * as React from 'react';
import { ReactWidget, Dialog, showDialog } from '@jupyterlab/apputils';
import * as actions from "@mrblenny/react-flow-chart/src/container/actions";
import styled from 'styled-components'
import { theme } from './Theme';
import { mapValues } from 'lodash';
import { Page, /* SidebarItem */ } from './components';
import { chartSimple } from './exampleChart';
import { FlowChart, IChart } from '@mrblenny/react-flow-chart';
import { ThemeProvider } from '@material-ui/core';
import { NodeCustom, NodeInnerCustom, PortCustom } from '@jupyter_vre/chart-customs';
import BasicSpeedDial from './components/SpeedDial';
import { CatalogDialog } from './components/CatalogDialog';
import { Workspace } from './components/Workspace';
import { FairCell, requestAPI } from '@jupyter_vre/core';
import { CellEditor } from './components/CellEditor';
import { Parallelization } from './components/Parallelization';

const CenterContent = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
`

interface IProps { }

interface IState {
	chart: IChart
}

export const DefaultState: IState = {
	chart: chartSimple,
}


class Composer extends React.Component<IProps, IState> {

	state = DefaultState

	workspaceRef: React.RefObject<Workspace>;

	constructor(props: IProps) {
		super(props);
		this.workspaceRef = React.createRef();
	}

	handleAddCellToWorkspace = (cell: FairCell) => {
		this.workspaceRef.current.addElement(cell);
	}

	handleIsCellInWorkspace = (cell: FairCell) => {
		return this.workspaceRef.current.hasElement(cell);
	}

	getWorkspaceElementFromChartId = (chartId: string): FairCell => {

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

	chartStateActions = mapValues(actions, (func: any) =>
		(...args: any) => {
			let newChartTransformer = func(...args);
			let newChart = newChartTransformer(this.state.chart);
			this.setState({
				chart: { ...this.state.chart, ...newChart }
			});
		}) as typeof actions

	handleDialSelection = (operation: string) => {

		switch (operation) {

			case "cells-catalogs":
				showDialog(this.CatalogDialogOptions);
				break;

			case "export-workflow":
				this.exportWorkflow();
				break;
		}
	}

	exportWorkflow = async () => {

		let resp = await requestAPI<any>('workflow/export', {
			body: JSON.stringify(this.state.chart),
			method: 'POST'
		});

		console.log(resp);
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
						<BasicSpeedDial
							handleDialSelection={this.handleDialSelection}
						/>
					</CenterContent>
				</Page>
			</ThemeProvider>
		)
	}
}

export class ComposerWidget extends ReactWidget {

	constructor() {
		super();
		this.addClass('vre-composer');
	}

	render(): JSX.Element {
		return (
			<Composer />
		);
	}
}