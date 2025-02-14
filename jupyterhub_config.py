# Basic Authentication Configuration
c.JupyterHub.authenticator_class = 'jupyterhub.auth.PAMAuthenticator'

# Define allowed users explicitly
c.Authenticator.allowed_users = {'arthrod', 'guest', 'pc', 'fortuna'}
c.Authenticator.admin_users = {'arthrod'}  # Make arthrod an admin

# Allow users to add/remove other users once added
c.Authenticator.allow_existing_users = True

# Enable sharing capabilities
c.JupyterHub.load_roles = [
    {
        "name": "user",
        "scopes": [
            "self",
            "shares!user",
            "read:users:name",
            "read:groups:name"
        ],
    },
    {
        "name": "admin",
        "groups": ["admin"],
        "scopes": [
            "admin:users",
            "admin:servers",
            "admin:groups",
            "list:users",
            "list:servers",
            "read:users:activity",
            "read:users:name",
            "read:users:groups",
            "read:groups:name",
        ],
        "users": ["arthrod"]
    }
]

# Enable server sharing capabilities
c.Spawner.oauth_client_allowed_scopes = ["access:servers!server", "shares!server"]

# Groups configuration
c.JupyterHub.load_groups = {
    "admin": ["arthrod"],
    "users": ["arthrod", "guest", "pc", "fortuna"],
    "collaborative": {"users": []},
}
