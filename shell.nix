let
  config = {
    # allowUnfree = true;
  };
  pkgs =
    import (fetchTarball "https://github.com/NixOS/nixpkgs/archive/refs/heads/nixos-25.05.tar.gz")
      { inherit config; };
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    uv
  ];
}
