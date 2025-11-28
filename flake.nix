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
            pkgs.nodejs_20
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
             
            source env/bin/activate
          '';
        };
      });
}

