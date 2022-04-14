import * as React from 'react';
import { ReactWidget, Dialog, showDialog } from '@jupyterlab/apputils';
import * as actions from "@mrblenny/react-flow-chart/src/container/actions";
import styled from 'styled-components'
import { theme } from './Theme';
import { mapValues } from 'lodash';
import { Page, /* SidebarItem */ } from './components';
import { chartSimple } from './exampleChart';
import { FlowChart, IChart } from '@mrblenny/react-flow-chart';
import { /* Button,*/ Slider, ThemeProvider } from '@material-ui/core';
import { NodeInnerCustom, PortCustom } from '@jupyter_vre/chart-customs';
import { requestAPI } from '@jupyter_vre/core';
import BasicSpeedDial from './components/SpeedDial';
import { CatalogDialog } from './components/CatalogDialog';

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

const CatalogDialogOptions: Partial<Dialog.IOptions<any>> = {
	title: 'Explore Catalog',
	body: ReactWidget.create(<CatalogDialog />) as Dialog.IBodyWidget<any>,
	buttons: []
};

class Composer extends React.Component<IProps, IState> {

	state = DefaultState

	chartStateActions = mapValues(actions, (func: any) =>
		(...args: any) => {
			let newChartTransformer = func(...args);
			let newChart = newChartTransformer(this.state.chart);
			this.setState({
				chart: { ...this.state.chart, ...newChart }
			});
		}) as typeof actions

	constructor(props: IProps) {
		super(props);
	}

	handleDialSelection = (operation: string) => {
		
		switch (operation) {

			case "open-catalog":
				showDialog(CatalogDialogOptions)
			break;

			case "export-workflow":
			break;
		}
	}

	handleChangeScalingFactor = (e: React.ChangeEvent<{}>, newValue: number | number[], node_id: string) => {
		
		let newNodes = this.state.chart.nodes
		newNodes[node_id].properties['scalingFactor'] = newValue

		this.setState({
			chart: {
				...this.state.chart,
				nodes: newNodes
			}
		})
	}

	exportWorkflow = async () => {

		const resp = await requestAPI<any>('workflow/export', {
            body: JSON.stringify(this.state.chart),
            method: 'POST'
        });

		console.log(resp);
	}

	getNodeEditor(): JSX.Element {

		let id_sel = this.state.chart.selected.id;
		let node = this.state.chart.nodes[id_sel];
		
		if (node.type == "splitter" || node.type == "merger") {
			return (
				<div>
					<p>Scaling Factor:</p>
					<Slider
						onChange={(e, nv) => { this.handleChangeScalingFactor(e, nv, node.id) }}
						defaultValue={1}
						value={node.properties['scalingFactor']}
						aria-labelledby="discrete-slider"
						valueLabelDisplay="auto"
						step={1}
						marks
						min={1}
						max={100}
					/>
				</div>
			);
		}

		return (
			<p>{node.properties['title']}</p>
		);
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
								NodeInner: NodeInnerCustom,
								Port: PortCustom
							}}
						/>
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