import * as React from 'react';
import { ReactWidget } from '@jupyterlab/apputils';
import { theme } from './Theme';
import { requestAPI } from '@jupyter_vre/core';
import { Button, Card, CardContent, FormControl, InputLabel, MenuItem, Select, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, ThemeProvider, Typography } from '@material-ui/core';

interface IProps {  }

interface IState {
	provision_template	: string
	loading				: boolean
	credentials			: []
	sel_cred			: string
	deployments			: Object[]
}

export const DefaultState: IState = {
	provision_template	: '',
	loading				: false,
	credentials			: [],
	sel_cred			: '',
	deployments			: []
}

class InfrastructureAutomator extends React.Component<IProps, IState> {

	state = DefaultState

	constructor(props: IProps) {
		super(props);
		// this.loadCredentials();
	}

	loadCredentials = async () => {

		const resp = await requestAPI<any>('sdia/credentials', { 
			method: 'GET' 
		});
		
		console.log(resp);
		this.setState({ credentials: resp });
	}

	handleProvisionTemplateChange = (event: React.ChangeEvent<{ value: unknown }>) => {
		
		this.setState({ provision_template: event.target.value as string });
	};

	handleSelCredChange = (event: React.ChangeEvent<{ value: unknown }>) => {
		
		this.setState({ sel_cred: event.target.value as string });
	};

	handleProvisionClick = async () => {
		
		this.setState({ loading: true });

		const resp = await requestAPI<any>('catalog/provision/add', {
			body: JSON.stringify({
				credential: this.state.sel_cred,
				provision_template: this.state.provision_template
			}),
			method: 'POST'
		});

		this.setState({ loading: false });
		console.log(resp);
	};

	render() {
		return (
			<ThemeProvider theme={theme}>
				<div>
					<Card className={'conf-card'}>
						<CardContent>
							<Typography className={'conf-title'}>
								SDIA Credentials
							</Typography>
							<FormControl className={'conf-form'}>
								<InputLabel>Select Credentials</InputLabel>
								<Select
									value={this.state.sel_cred}
									onChange={this.handleSelCredChange}
								>
									<MenuItem value={''}>-- None --</MenuItem>
								{ this.state.credentials.map((cred: any) => (
									<MenuItem value={cred['username']}>{cred['username']} - {cred['endpoint']}</MenuItem>
								))}
								</Select>
							</FormControl>
						</CardContent>
					</Card>
					{ this.state.sel_cred ? (<div>
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
									<MenuItem value={'6183b6700ef9ab0975655b87'}>2 VMs (Argo on K8s)</MenuItem>
								</Select>
							</FormControl>
							<br />
							<Button variant='contained'
									className={'btn-prov'}
									color='primary'
									disabled={this.state.provision_template == ''}
									onClick={this.handleProvisionClick}>
										Provision
							</Button>
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
					</div>) : (<div></div>) }
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
