import * as React from 'react';

export class SDIAAuthDialog extends React.Component {

    constructor(props: any) {
        super(props);
    }

    render(): React.ReactElement {
        return (
            <form className={'sdia-auth-form'}>
                <label htmlFor='sdia-auth-username'>Username:</label>
                <br/>
                <input
                    type='text'
                    className='auth-form'
                    id='sdia-auth-username'
                    name='sdia-auth-username'
                />
                <br/>
                <label htmlFor='sdia-auth-password'>Password:</label>
                <br/>
                <input
                    type='password'
                    className='auth-form'
                    id='sdia-auth-password'
                    name='sdia-auth-password'
                />
                <br/>
                <label htmlFor='sdia-auth-endpoint'>Endpoint:</label>
                <br/>
                <input
                    type='url'
                    className='auth-form'
                    id='sdia-auth-endpoint'
                    name='sdia-auth-endpoint'
                />
            </form>
        )
    }
}