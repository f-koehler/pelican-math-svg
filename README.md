# math-svg: A Plugin for Pelican

[![Build Status](https://img.shields.io/github/workflow/status/f-koehler/pelican-math-svg/build)](https://github.com/f-koehler/pelican-math-svg/actions)
[![PyPI Version](https://img.shields.io/pypi/v/pelican-math-svg)](https://pypi.org/project/pelican-math-svg/)
![License](https://img.shields.io/pypi/l/pelican-math-svg?color=blue)

Render math expressions to svg and embed them.

## Installation

This plugin can be installed via:

```shell
python -m pip install pelican-math-svg
```

## Requirements

-   required LaTeX tools (all included in TeX Live and possibly other LaTeX distributions):
    -   `lualatex` (or another LaTeX compiler if changed in the settings, [see below](#configuration))
    -   `pdfcrop`
    -   `dvisvgm`
-   `scour` (optional)
-   `svgo` (optional)

## Usage

In Markdown you can use `$x$` for inline math and

```
$$
  \int x^2
$$
```

for display math.

It is required to set the stroke color using the `strokeonly` class (this class name can be changed, see [configuration options below](#configuration)), otherwise lines would be rendered white:

```css
svg path.strokeonly {
    color: #000;
}
```

To change the fill color for equations as well, thus essential changing the default color for math, specify the following additionally:

```css
span.math svg path,
div.math svg path {
    fill: #000;
}
```

## Configuration

In your `pelicanconf.py` you can use the following options to tweak the behavior of the plugin:

| Setting                         | Description                                                                                                                 | Default Value                                                                                                                                       |
| ------------------------------- | --------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| `MATH_SVG["titles"]             | Whether to generate `<title>` tags containing the raw LaTeX code (recommended for accessibility).                           | `True`                                                                                                                                              |
| `MATH_SVG["scale_inline"]`      | scaling factor for inline math                                                                                              | `1.0`                                                                                                                                               |
| `MATH_SVG["scale_display"]`     | scaling factor for display math                                                                                             | `1.0`                                                                                                                                               |
| `MATH_SVG["strokeonly_class]`   | CSS class for SVG paths that have no filling and a black stroke color, useful when changing the color of rendered equations | `strokeonly`                                                                                                                                        |
| `MATH_SVG["latex"]["args"]`     | CLI arguments of the invoked LaTeX compiler                                                                                 | `"--interaction=errorstopmode", "--halt-on-error"`                                                                                                  |
| `MATH_SVG["latex"]["preamble"]` | preamble of the generated LaTeX document                                                                                    | `[r"\documentclass[preview,border={2pt 0pt}]{standalone}",r"\usepackage{amsmath}",r"\usepackage{amssymb}",]`                                        |
| `MATH_SVG["latex"]["program"]`  | LaTeX compiler to use                                                                                                       | `lualatex`                                                                                                                                          |
| `MATH_SVG["pdfcrop"]["args"]`   | CLI arguments for `pdfcrop`                                                                                                 | `--hires`                                                                                                                                           |
| `MATH_SVG["dvisvgm"]["args"]`   | CLI arguments for `dvisvgm`                                                                                                 | `["--pdf", "--optimize=all", "--no-fonts", "--exact-bbox"]`                                                                                         |
| `MATH_SVG["scour"]["args"]`     | CLI arguments for `scour`                                                                                                   | `["--strip-xml-prolog", "--remove-descriptions", "--remove-metadata", "--enable-comment-stripping", "--strip-xml-space", "--enable-id-stripping",]` |
| `MATH_SVG["scour"]["enabled"]`  | whether to use `scour` to optimize SVG output                                                                               | `True` if `scour` is in `$PATH`, `False` otherwise                                                                                                  |
| `MATH_SVG["svgo"]["args"]`      | CLI arguments for `svgo`                                                                                                    | `["--multipass", "--precision", "5"]`                                                                                                               |
| `MATH_SVG["svgo"]["enabled"]`   | whether to use `svgo` to optimize SVG output                                                                                | `True` if `svgo` is in `$PATH`, `False` otherwise                                                                                                   |

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

[existing issues]: https://github.com/f-koehler/pelican-math-svg/issues
[contributing to pelican]: https://docs.getpelican.com/en/latest/contribute.html

## License

This project is licensed under the GPLv3 license.
