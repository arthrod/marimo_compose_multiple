{
  description = "JupyterHub with Marimo Integration";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            python3
            python3Packages.pip
            python3Packages.jupyterhub
            python3Packages.notebook
            python3Packages.jupyterlab
            docker
            docker-compose
            uv
          ];

          shellHook = ''
            export PYTHONPATH="$PWD:$PYTHONPATH"
            export JUPYTERHUB_CONFIG_DIR="$PWD/jupyterhub"
            export PATH="$PWD/bin:$PATH"
          '';
        };

        packages.default = pkgs.dockerTools.buildImage {
          name = "jupyterhub-marimo";
          tag = "latest";
          
          copyToRoot = pkgs.buildEnv {
            name = "image-root";
            paths = with pkgs; [
              bash
              coreutils
              python3
              python3Packages.jupyterhub
              python3Packages.notebook
              python3Packages.jupyterlab
              python3Packages.marimo
              docker
            ];
          };

          config = {
            Cmd = [ "jupyterhub" "-f" "/srv/jupyterhub/jupyterhub_config.py" ];
            WorkingDir = "/srv/jupyterhub";
            ExposedPorts = {
              "8000/tcp" = {};
            };
            Volumes = {
              "/srv/jupyterhub" = {};
              "/shared" = {};
            };
          };
        };
      }
    );
}
