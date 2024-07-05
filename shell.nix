with import <nixpkgs> {};
with pkgs.python3Packages;

buildPythonPackage rec {
  name = "sportsteam";
  src = ./.;
  propagatedBuildInputs = [ django_4 icalendar numpy ];
}
