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

  outputs = { self, nixpkgs, flake-utils, uv2nix, pyproject-nix, pyproject-build-systems, ... }: let
    mkPythonApp = import ./mkPythonApp.nix {
      inherit self nixpkgs flake-utils uv2nix pyproject-nix pyproject-build-systems;
    };

  in
    mkPythonApp
      (pkgs: pkgs.python312)  # python version
      "tscrb"                 # pyproject project name 
      [ "tscrb" "zboub" ];    # pyproject.scripts
}
