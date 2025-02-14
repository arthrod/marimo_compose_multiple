# JupyterHub with Marimo Integration

A JupyterHub deployment with Marimo integration, GitHub OAuth authentication, and Docker Spawner for isolated user environments.

## Features

- GitHub OAuth authentication
- Docker-based user environments
- Marimo integration with shared workspace support
- Named servers support (multiple environments per user)
- PostgreSQL for persistent state
- Coolify deployment ready

## Setup Instructions

1. **GitHub OAuth Setup**
   - Create a new GitHub OAuth application at https://github.com/settings/developers
   - Set the callback URL to `https://<your-domain>/hub/oauth_callback`
   - Note down the Client ID and Client Secret

2. **Environment Variables**
   Create a `.env` file with the following variables:

   ```env
   # GitHub OAuth
   GITHUB_CLIENT_ID=<your-github-client-id>
   GITHUB_CLIENT_SECRET=<your-github-client-secret>
   OAUTH_CALLBACK_URL=https://<your-domain>/hub/oauth_callback

   # JupyterHub Configuration
   JH_COOKIE_SECRET=<generate-random-hex>
   JH_CRYPT_KEY=<generate-random-hex>
   JH_DOMAIN=<your-domain>
   JH_SUBDOMAIN=jupyter
   JH_CERTRESOLVER_NAME=default

   # PostgreSQL Configuration
   POSTGRES_DB=jupyterhub
   POSTGRES_USER=jupyterhub
   POSTGRES_PASSWORD=<strong-password>
   ```

3. **Deployment on Coolify**
   - Push this repository to your Git provider
   - In Coolify:
     1. Create a new service
     2. Select "Docker Compose"
     3. Point to your repository
     4. Set the environment variables as defined above
     5. Deploy!

## Deployment with Coolify and Nix

### Prerequisites
- Coolify instance
- Nix package manager (will be installed by Coolify if not present)

### Deployment Steps

1. **Nix Environment Setup**
   The repository includes:
   - `flake.nix`: Defines the development environment and container build
   - `shell.nix`: Provides compatibility with older Nix installations

2. **Environment Variables**
   Set the following in Coolify:
   ```env
   GITHUB_CLIENT_ID=<your-github-client-id>
   GITHUB_CLIENT_SECRET=<your-github-client-secret>
   OAUTH_CALLBACK_URL=https://<your-domain>/hub/oauth_callback
   ```

3. **Coolify Deployment**
   - Create a new service in Coolify
   - Select "Docker Compose with Nix"
   - Point to your repository
   - Set the environment variables
   - Deploy!

The Nix configuration will:
- Set up all required Python packages and dependencies
- Configure JupyterHub with GitHub authentication
- Set up Docker for container management
- Configure Marimo integration and shared workspace

### Development

For local development with Nix:
```bash
# Enter development shell
nix develop

# Or with legacy Nix
nix-shell

# Start JupyterHub
docker-compose up
```

## Usage

1. Access your JupyterHub instance at `https://<your-domain>`
2. Log in with your GitHub account
3. You can create multiple named servers for different purposes
4. Use the shared workspace at `/shared` for collaborative work
5. Marimo notebooks are automatically supported

## User Groups and Access Control

The system is configured with the following user groups:

- **Admin Group**: Administrators with full system access
  - Members: `arthrod`
  - Permissions: Full admin access, including user management and server control

- **Users Group**: Regular users with standard access
  - Members: `arthrod`, `guest`, `pc`, `fortuna`
  - Permissions: Can create and manage their own servers, access shared workspaces

- **Collaborative Group**: For shared workspace access
  - Members: Configurable through admin interface
  - Permissions: Access to collaborative features and shared notebooks

## Architecture

- JupyterHub manages authentication and spawns user containers
- Each user gets their own Docker container with JupyterLab
- Marimo integration provides enhanced notebook capabilities
- PostgreSQL stores JupyterHub state
- Docker volumes persist user data
- Shared volume enables collaboration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - See LICENSE file for details
