import * as React from 'react';


interface IState {

}

interface GitHubCredPanelProps {

}

const DefaultState: IState = {

}


export class GitHubCredPanel extends React.Component<GitHubCredPanelProps, IState> {

    state = DefaultState;

    render(): React.ReactElement {
        return (
            <div>GitHub Credentials</div>
        )
    }
}