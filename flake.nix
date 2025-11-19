{
  description = "Python CLI to transcribe audio files using AI transcription APIs.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";
    flake-utils.url = "github:numtide/flake-utils";

    pyproject-nix = {
      url = "github:pyproject-nix/pyproject.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };

    uv2nix = {
      url = "github:pyproject-nix/uv2nix";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        pyproject-nix.follows = "pyproject-nix";
      };
    };

    pyproject-build-systems = {
      url = "github:pyproject-nix/build-system-pkgs";
      inputs = {
        nixpkgs.follows = "nixpkgs";
        pyproject-nix.follows = "pyproject-nix";
      };
    };
  };

  outputs = { self, nixpkgs, flake-utils, uv2nix, pyproject-nix, pyproject-build-systems, ... }:
    let
      mkPythonApp = { self, nixpkgs, flake-utils, uv2nix, pyproject-nix, pyproject-build-systems, ... }:
        flake-utils.lib.eachDefaultSystem (system:
          let 
            pkgs = import nixpkgs { inherit system; };
            python = pkgs.python312;

            workspace = uv2nix.lib.workspace.loadWorkspace {
              workspaceRoot = ./.;
            };

            uvLockedOverlay = workspace.mkPyprojectOverlay {
              sourcePreference = "wheel";  # Or "sdist" ??
            };

            pythonSet =
              (pkgs.callPackage pyproject-nix.build.packages { inherit python; })
              .overrideScope (nixpkgs.lib.composeManyExtensions [
                pyproject-build-systems.overlays.default  # Build tools
                uvLockedOverlay  # Locked dependencies
              ]);

            projectName = "tscrb";
            binaries = [ "tscrb" "zboub" ];
            projectPkg = pythonSet.${projectName};

            pythonEnvName = projectName + "-env";
            pythonEnv = pythonSet.mkVirtualEnv pythonEnvName workspace.deps.default;

            inherit (pkgs.callPackages pyproject-nix.build.util { }) mkApplication;

          in {
            devShells.default = pkgs.mkShell {
              name = projectName;
              packages = [
                pythonEnv
                pkgs.python312  # FIXME: Needed to add this for uv to find python in shell
                pkgs.ruff
                pkgs.uv
              ];

              shellHook = ''
                uv sync
              '';

              # Needed for Jupyter Lab
              LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
                pkgs.stdenv.cc.cc.lib
                pkgs.zeromq
              ];

              # Fix for opening tmux in nix-shell env
              SHELL = "${pkgs.bashInteractive}/bin/bash";
            };


            packages.default = mkApplication {
              venv = pythonEnv;
              package = projectPkg;
            };
            packages.${projectPkg.pname} = self.packages.${system}.default;


            apps = builtins.listToAttrs (map
              (bin: {
                name = bin;
                value = {
                  type = "app";
                  program = "${self.packages.${system}.default}/bin/${bin}";
                };
              })
              binaries
            ) // {
              default = self.apps.${system}.${projectPkg.pname};
            };
          }
        );
  in
    mkPythonApp {
      inherit self nixpkgs flake-utils uv2nix pyproject-nix pyproject-build-systems;
    };
}
