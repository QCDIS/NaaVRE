import * as React from 'react';

export class GithubAuthDialog extends React.Component {

    constructor(props: any) {
        super(props);
    }

    render(): React.ReactElement {
        return (
            <form className={'github-auth-form'}>
                <label htmlFor='github-auth-token'>Token:</label>
                <br/>
                <input
                    type='password'
                    className='auth-form'
                    id='github-auth-token'
                    name='github-auth-token'
                />
            </form>
        )
    }
}