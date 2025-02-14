# GitHub OAuth Configuration
c.JupyterHub.authenticator_class = 'oauthenticator.GitHubOAuthenticator'
c.GitHubOAuthenticator.oauth_callback_url = os.environ.get('OAUTH_CALLBACK_URL')
c.Authenticator.admin_users = {'arthrod'}

# Groups configuration
c.JupyterHub.load_groups = {
    "admin": ["arthrod"],
    "users": ["arthrod", "guest", "pc", "fortuna"],
    "collaborative": {"users": []},
}

# Docker spawner configuration
c.JupyterHub.spawner_class = 'dockerspawner.DockerSpawner'
c.DockerSpawner.image = 'jupyter/base-notebook:latest'
c.DockerSpawner.network_name = os.environ.get('DOCKER_NETWORK_NAME', 'hubnet')
c.DockerSpawner.remove = True

# Marimo configuration
c.Spawner.default_url = '/lab'
c.Spawner.cmd = ['jupyter-labhub']
c.Spawner.environment = {
    'MARIMO_WORKSPACE': '{username}',
    'MARIMO_SHARED': '/shared'
}

# Volume mounts for user data persistence
c.DockerSpawner.volumes = {
    'jupyterhub-user-{username}': '/home/jovyan/work',
    'shared': '/shared'
}

# Allow named servers
c.JupyterHub.allow_named_servers = True
c.JupyterHub.named_server_limit_per_user = 2

# Services
c.JupyterHub.services = [
    {
        'name': 'marimo-proxy',
        'url': 'http://127.0.0.1:9000',
        'command': ['jupyter-marimo-proxy'],
        'environment': {
            'MARIMO_SHARED': '/shared'
        }
    }
]
