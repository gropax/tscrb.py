{
  description = "Python CLI to transcribe audio files using AI transcription APIs.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.05";

    python-utils = {
      url = "github:gropax/python-utils.nix";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, python-utils, ... }:
    let
      base = python-utils.lib.mkPythonApp
        (pkgs: pkgs.python312)  # python version
        "tscrb"                 # pyproject project name 
        ./.                     # project dir
        [ "tscrb" "zboub" ];    # pyproject.scripts
    in
    {
      devShells = base.devShells;
      packages = base.packages;
      apps = base.apps;
    };
}
