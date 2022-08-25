
0.10.1 - 2022-08-25
-------------------

Fix empty SVG files.

`dvisvgm` is incompatible with the new PDF interpreter in `gs` that has become the default in version 9.56.0.
This has been taken into account in `dvisvgm` which unfortunately is not part of the latest TeXLive release.
As a workaround we force `gs` to use the old PDF interpreter by setting an environment variable.
