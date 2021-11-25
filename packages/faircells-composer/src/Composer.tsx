import * as React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import * as actions from "@mrblenny/react-flow-chart/src/container/actions";
import styled from 'styled-components'
import { theme } from './Theme';
import { mapValues } from 'lodash';
import { Page, SidebarItem } from './components';
import { chartSimple } from './exampleChart';
import { FlowChart, IChart } from '@mrblenny/react-flow-chart';
import { Button, Slider, ThemeProvider } from '@material-ui/core';
import { NodeInnerCustom, PortCustom } from '@jupyter_vre/chart-customs';
import { requestAPI } from '@jupyter_vre/core';
import { SidebarSpecialItem } from './components/SidebarSpecialItem';

const LeftContent = styled.div`
  display: flex;
  flex-direction: column;
  flex: 0 0 230px;
  overflow: hidden;
`

const CenterContent = styled.div`
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
`

const RightContent = styled.div`
  display: flex;
  flex-direction: column;
  flex: 0 0 400px;
  overflow: hidden;
`

const CatalogSidebar = styled.div`
	width: 100%;
	background: white;
	position: relative;
	margin: 0;
	display: flex;
	flex-direction: column;
	flex-shrink: 0;
	`

const InfoSidebar = styled.div`
	width: 215px;
	background: white;
	position: absolute;
	margin: 20px;
	display: flex;
	flex-direction: column;
	flex-shrink: 0;
	`

const Message = styled.div`
	padding: 10px;
	text-align: center;
	color: white;
	font-weight: bold;
	font-size: larger;
	background: lightslategrey;
	`

interface IProps { }

interface IState {
	catalog_elements: []
	chart: IChart
}

export const DefaultState: IState = {
	catalog_elements: [],
	chart: chartSimple,
}

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

	componentDidMount() {
		this.getCatalog();
	}

	getCatalog = async () => {

		const resp = await requestAPI<any>('catalog/cells/all', {
			method: 'GET'
		});

		this.setState({ catalog_elements: resp });
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
					<LeftContent>
						<CatalogSidebar>
							<Message>
								Local Catalog
							</Message>
							<div className={'sidebar-items-container'}>
								{this.state.catalog_elements.map((value, index) => {
									let nodes = value['chart_obj']['nodes']
									let element = nodes[Object.keys(nodes)[0]]
									return (
										<SidebarItem
											type={element['type']}
											ports={element['ports']}
											properties={element['properties']}
										/>
									)
								})}
							</div>
						</CatalogSidebar>
						<CatalogSidebar>
							<Message>
								Scaling Nodes
							</Message>
							<div className={'sidebar-items-container'}>
								<SidebarSpecialItem
									type={'splitter'}
									ports={{
										splitter_source: {
											id: 'splitter_source',
											type: 'left',
											properties: {
												special_node: 1,
												color: '#000000'
											}
										},
										splitter_target: {
											id: 'splitter_target',
											type: 'right',
											properties: {
												special_node: 1,
												color: '#000000'
											}
										}
									}}
									properties={{
										'title': 'Splitter',
										'scalingFactor': 1
									}}
								/>
								<SidebarSpecialItem
									type={'merger'}
									ports={{
										merger_source: {
											id: 'merger_source',
											type: 'left',
											properties: {
												special_node: 1,
												color: '#000000'
											}
										},
										merger_target: {
											id: 'merger_target',
											type: 'right',
											properties: {
												special_node: 1,
												color: '#000000'
											}
										}
									}}
									properties={{
										'title': 'Merger',
										'scalingFactor': 1
									}}
								/>
							</div>
						</CatalogSidebar>
						<div>
							<Button 
								className={'btn-export-workflow'} 
								variant="contained" 
								color="primary"
								onClick={this.exportWorkflow}
								>
								Export Workflow
							</Button>
						</div>
					</LeftContent>
					<CenterContent>
						<FlowChart
							chart={this.state.chart}
							callbacks={this.chartStateActions}
							Components={{
								NodeInner: NodeInnerCustom,
								Port: PortCustom
							}}
						/>
					</CenterContent>
					{ this.state.chart.selected.id && this.state.chart.selected.type == "node" ? (
					<RightContent>
						<InfoSidebar>
							<div className={'info-sidebar-container'}>
								<div>{this.getNodeEditor()}</div>
							</div>
						</InfoSidebar>
					</RightContent>)
					: (<div></div>) }
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