{
  description = "PHX - Brighton Phoenix Django development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
  };

  outputs = { self, nixpkgs, nixpkgs-python, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs {
          inherit system;
        };

        python = nixpkgs-python.packages.${system}."3.12";
        pythonEnv = python.withPackages (ps: with ps; [
          pip
          virtualenv
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = [
            pythonEnv
            pkgs.nodejs_21
            pkgs.postgresql_15
            pkgs.podman
            pkgs.podman-compose
          ];

          shellHook = ''
            echo "🐍 Python $(python --version)"
            echo "📦 Node.js $(node --version)"
            echo "📦 npm $(npm --version)"
            echo ""

            # Create virtual environment if it doesn't exist
            if [ ! -d "env" ]; then
                virtualenv env
                echo "✓ Created virtual environment"
                # Install pip-tools in the virtualenv (not in Nix store)
                env/bin/pip install pip-tools
            fi

            # Start postgres if not running using podman-compose
            if ! podman ps --format "{{.Names}}" | grep -q "^phx-postgres$"; then
              echo "🗄️  Starting PostgreSQL..."
              podman-compose up -d
              echo "✓ PostgreSQL started"
            else
              echo "🗄️  PostgreSQL is already running"
            fi
            echo ""
            
            source env/bin/activate
          '';
        };
      });
}

