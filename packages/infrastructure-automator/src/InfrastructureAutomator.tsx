import * as React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { theme } from './Theme';
import { requestAPI } from '@jupyter_vre/core';
import { Button, Card, CardContent, CircularProgress, FormControl, InputLabel, MenuItem, Select, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, TextField, ThemeProvider, Typography } from '@material-ui/core';

interface IProps {  }

interface IState {
	provision_template	: string
	loading				: boolean
	deployments			: Object[]
}

export const DefaultState: IState = {
	provision_template	: '',
	loading				: false,
	deployments			: []
}

class InfrastructureAutomator extends React.Component<IProps, IState> {

	state = DefaultState

	constructor(props: IProps) {
		super(props);
	}

	handleProvisionTemplateChange = (event: React.ChangeEvent<{ value: unknown }>) => {

		let newValue = (event.target.value == 'custom') ? 'custom' : event.target.value
		this.setState({ provision_template: newValue as string });
	};

	handleProvisionClick = async () => {
		
		this.setState({ loading: true });

		await requestAPI<any>('catalog/provision/add', {
			body: JSON.stringify({
				privision_template: this.state.provision_template
			}),
			method: 'POST'
		});

		setTimeout(() => {
			let deployment = {
					name		: 'sdia_4wokmyp9',
					platform	: 'Amazon Web Services',
					vms			: 2,
					dashboard	: 'http://79.125.48.148:31258'
				};
			let newDeployments = this.state.deployments;
			newDeployments.push(deployment)
			this.setState({ loading: false, deployments: newDeployments });
		}, 5000);
	};

	render() {
		return (
			<ThemeProvider theme={theme}>
				<div>
				<Card className={'conf-card'}>
					<CardContent>
						<Typography className={'conf-title'}>
							Infrastructure Configuration
						</Typography>
						<FormControl className={'conf-form'}>
							<InputLabel>Provision Template</InputLabel>
							<Select
								value={this.state.provision_template}
								onChange={this.handleProvisionTemplateChange}
							>
								<MenuItem value={''}>-- None --</MenuItem>
								<MenuItem value={'615f18ecaf8ebb245af0b09c'}>Standard</MenuItem>
								<MenuItem value={'custom'}>Custom</MenuItem>
							</Select>
						</FormControl>
						{ (this.state.provision_template == 'custom') ? (
							<div className={'custom-prov-container'}>
								<TextField
									className="custom-prov-form"
									label="Custom ID"
									variant="outlined"
									onChange={this.handleProvisionTemplateChange}
									value={this.state.provision_template}
								/>
							</div>
						) : (<div></div>) }
						<br />
						<Button variant='contained'
								className={'btn-prov'}
								color='primary'
								disabled={this.state.provision_template == ''}
								onClick={this.handleProvisionClick}>
									Provision
						</Button>
						{this.state.loading ? (
							<span>
								<CircularProgress className={'add-catalog-progress'} size={30}/>
							</span>
						) :(<span></span>)}
					</CardContent>
				</Card>
				<Card className={'conf-card'}>
					<CardContent>
						<Typography className={'conf-title'}>
							Active Deployments
						</Typography>
						<TableContainer component={Card} className={'lw-deploy-table'}>
                            <Table aria-label="simple table">
							<TableHead>
								<TableRow>
									<TableCell><b>Cluster</b></TableCell>
									<TableCell align="center"><b>Platform</b></TableCell>
									<TableCell align="center"><b>VMs</b></TableCell>
									<TableCell align="center"><b>Dashboard</b></TableCell>
								</TableRow>
							</TableHead>
                                <TableBody>
								{this.state.deployments.map((dep: any) => (
									<TableRow>
										<TableCell component="th" scope="row">{dep.name}</TableCell>
										<TableCell component="th" scope="row">{dep.platform}</TableCell>
										<TableCell component="th" scope="row">{dep.vms}</TableCell>
										<TableCell component="th" scope="row">
											<a target="_blank" href={dep.dashboard}>Argo</a>
											</TableCell>
									</TableRow>
                                ))}
                            </TableBody>
                            </Table>
                        </TableContainer>
					</CardContent>
				</Card>
				</div>
			</ThemeProvider>
		)
	}
}

export class InfrastructureAutomatorWidget extends ReactWidget {

	constructor() {
		super();
		this.addClass('vre-infrastructure-automator');
	}

	render(): JSX.Element {
		return (
			<InfrastructureAutomator />
		);
	}
}
