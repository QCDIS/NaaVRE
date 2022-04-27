import * as React from 'react';

export class ImageRegistryAuthDialog extends React.Component {

    constructor(props: any) {
        super(props);
    }

    render(): React.ReactElement {
        return (
            <form className={'image-registry-auth-form'}>
                <label htmlFor='image-registry-url'>Image Registry url:</label>
                <br/>
                <input
                    type='url'
                    className='auth-form'
                    id='image-registry-url'
                    name='image-registry-url'
                />
                {/* <br/>
                <label htmlFor='image-registry-auth-token'>Token:</label>
                <br/>
                <input
                    type='password'
                    className='auth-form'
                    id='image-registry-auth-token'
                    name='image-registry-auth-token'
                /> */}
            </form>
        )
    }
}