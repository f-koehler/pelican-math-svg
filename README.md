# math-svg: A Plugin for Pelican

[![PyPI Version](https://img.shields.io/pypi/v/pelican-math-svg)](https://pypi.org/project/pelican-math-svg/) ![License](https://img.shields.io/pypi/l/pelican-math-svg?color=blue)

Render math expressions to svg and embed them.

## Installation

This plugin can be installed via:

```shell
python -m pip install pelican-math-svg
```

This plugin depends `tex2svg` from the [`mathjax-node-cli`](https://github.com/mathjax/mathjax-node-cli) module that relies on the official [`MathJax-node`](https://github.com/mathjax/MathJax-node) module.
This can be easily installed using `yarn`

```shell
yarn global add mathjax-node-cli
```

or `npm`

```shell
npm install -g mathjax-node-cli
```

## Roadmap

-   [x] Markdown support
    -   [x] inline
    -   [x] display
-   [ ] RST support
    -   [ ] inline
    -   [ ] display
-   [x] cache rendered SVG
-   [ ] plugin settings
-   [ ] unit tests
-   [x] type annotations

## Contributing

Contributions are welcome and much appreciated. Every little bit helps. You can contribute by improving the documentation, adding missing features, and fixing bugs. You can also help out by reviewing and commenting on [existing issues][].

To start contributing to this plugin, review the [Contributing to Pelican][] documentation, beginning with the **Contributing Code** section.

[existing issues]: https://github.com/f-koehler/pelican-math-svg/issues
[contributing to pelican]: https://docs.getpelican.com/en/latest/contribute.html

## License

This project is licensed under the GPLv3 license.
