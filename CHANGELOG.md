
0.7.0 - 2021-08-20
------------------

Fix SVG paths that have `fill="none"` and a black stroke color by dropping the stroke attribute and adding a configurable CSS class.
This allows styling these elements, in particular changing the color.
However, as of now it is necessary to explicitly set the stroke color for these elements (see `README.md`) or they will not be visible.
