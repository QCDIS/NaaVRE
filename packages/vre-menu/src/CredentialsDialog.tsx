
import { Box, styled, Tab, Tabs, ThemeProvider } from '@material-ui/core';
import * as React from 'react';
import { theme } from './Theme';
import { TabPanel } from './TabPanel';
import { GitHubCredPanel } from './GitHubCredPanel';
import { requestAPI } from '@jupyter_vre/core';
import { WorkflowCredPanel } from './WorkflowCredPanel';

const CatalogBody = styled('div')({
    display: 'flex',
    overflow: 'hidden',
    flexDirection: 'row',
})

interface CatalogDialogProps { }

interface IState {
    selectedTab : number
    githubCredentials : []
    workflowCredentials : []
    registryCredentials : []
}

const DefaultState: IState = {
    selectedTab : 0,
    githubCredentials : [],
    workflowCredentials : [],
    registryCredentials : []
}

export class CredentialsDialog extends React.Component<CatalogDialogProps, IState> {

    state = DefaultState;

    handleTabChange(_event: React.ChangeEvent<{}>, newValue: number) {
        this.setState({ selectedTab: newValue });
    }

    getCredentials = async () => {

        const credentials = await requestAPI<any>('credentials', {
            method: 'GET'
        });

        const ghCred = credentials.filter((cred: any) => cred['provider'] == 'github');
        const wfCred = credentials.filter((cred: any) => cred['provider'] == 'argo');

        this.setState({ 
            githubCredentials   : ghCred,
            workflowCredentials : wfCred
        });
    }

    componentDidMount(): void {
        this.getCredentials();
    }

    render(): React.ReactElement {

        return (
            <ThemeProvider theme={theme}>
                <p className='section-header'>Manage Credentials</p>
                <CatalogBody>
                    <Box sx={{ width: '100%' }}>
                        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
                            <Tabs 
                                value={this.state.selectedTab}
                                onChange={(event, newValue) => this.handleTabChange(event, newValue)}
                            >
                                <Tab label="GitHub" />
                                <Tab label="Workflow Engine" />
                                <Tab label="Image Registry" />
                            </Tabs>
                        </Box>
                        <TabPanel value={this.state.selectedTab} index={0}>
                            <GitHubCredPanel credentials={this.state.githubCredentials}/>
                        </TabPanel>
                        <TabPanel value={this.state.selectedTab} index={1}>
                            <WorkflowCredPanel credentials={this.state.workflowCredentials} />
                        </TabPanel>
                        <TabPanel value={this.state.selectedTab} index={2}>
                            Item Three
                        </TabPanel>
                    </Box>
                </CatalogBody>
            </ThemeProvider>
        )
    }
}