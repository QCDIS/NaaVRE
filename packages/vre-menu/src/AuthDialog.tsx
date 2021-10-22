import { TextField } from '@material-ui/core';
import * as React from 'react';

export class AuthDialog extends React.Component {

    constructor(props: any) {
        super(props);
    }

    render(): React.ReactElement {
        return (
            <div>
                <form noValidate autoComplete="off">
                    <TextField
                        className="auth-form"
                        required id="standard-required" 
                        label="Username"
                        variant="outlined"
                    />
                    <br />
                    <TextField
                        className="auth-form"
                        id="standard-password"
                        type="password"
                        label="Password"
                        variant="outlined"
                    />
                </form>
            </div>
        )
    }
}