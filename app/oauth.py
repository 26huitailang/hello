from rauth import OAuth1Service, OAuth2Service
from flask import current_app, url_for, request, redirect, session

class OAuthSignIn(object):
    providers = None

    def __init__(self, provider_name):
        self.provider_name = provider_name
        credentials = current_app.config['OAUTH_CREDENTIALS'][provider_name]
        self.consumer_id = credentials['id']
        self.consumer_secret = credentials['secret']

    def authorize(self):
        pass

    def callback(self):
        pass

    def get_callback_url(self):
        return url_for('oauth_callback', provider=self.provider_name,
                       _external=True)

    @classmethod
    def get_provider(self, provider_name):
        if self.providers is None:
            self.providers = {}
            for provider_class in self.__subclasses__():
                provider = provider_class()
                self.providers[provider.provider_name] = provider
        return self.providers[provider_name]

class QQSignIn(OAuthSignIn):
    def __init__(self):
        super(QQSignIn, self).__init__('qq')
        self.service = OAuth2Service(
            name='qq',
            client_id=self.consumer_id,
            client_secret=self.consumer_secret,
            authorize_url='https://graph.qq.com/oauth2.0/authorize',
            access_token_url='https://graph.qq.com/oauth2.0/token',
            base_url='https://graph.qq.com/'
        )

    def authorize(self):
        return redirect(self.service.get_authorize_url(
            scope='email',
            response_type='code',
            redirect_uri=self.get_callback_url())
        )

    def callback(self):
        if 'code' not in request.args:
            return None, None, None
        oauth_session = self.service.get_auth_session(
            data={'code': request.args['code'],
                  'grant_type': self.get_callback_url()}
        )
        me = oauth_session.get('me').json()
        return (
            'qq$' + me['id'],
            me.get('email').split('@')[0],
            me.get('email')
        )


class FacebookSignIn(OAuthSignIn):
    pass

class TwitterSignIn(OAuthSignIn):
    pass