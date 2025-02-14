(import (
  fetchTarball {
    url = "https://github.com/edolstra/flake-compat/archive/master.tar.gz";
    sha256 = "0m4gx6ibqyr3cj6k0af9fjm0ydxg9wvl6fr52f3s2fg1kgj9v6l2";
  }
) {
  src = ./.;
}).shellNix
