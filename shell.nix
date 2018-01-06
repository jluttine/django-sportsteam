with import <nixpkgs> {};
with pkgs.python3Packages;

buildPythonPackage rec {
  name = "sportsteam";
  src = /home/jluttine/Workspace/django-sportsteam;
  propagatedBuildInputs = [ django icalendar ];
}
