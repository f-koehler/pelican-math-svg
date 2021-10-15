from functools import partial
import multiprocessing
from pathlib import Path

import typer

from pelican import get_instance, parse_arguments

from .database import Database
from .markdown_extension import render_svg
from .settings import PelicanMathSettings

app = typer.Typer()


@app.command()
def render(jobs: int = typer.Option(multiprocessing.cpu_count(), "-j")):
    pelican, _ = get_instance(parse_arguments([]))
    settings = PelicanMathSettings.from_settings(pelican)

    db = Database()

    missing = db.fetch_missing_inline()
    with multiprocessing.Pool(jobs) as pool:
        rendered = pool.map(
            partial(render_svg, inline=True, settings=settings),
            missing,
        )
    for equation, render in zip(missing, rendered):
        db.add_equation(True, equation, settings, render)
    print(f"rendered {len(rendered)} inline equations")

    missing = db.fetch_missing_inline()
    with multiprocessing.Pool(jobs) as pool:
        rendered = pool.map(
            partial(render_svg, inline=False, settings=settings),
            missing,
        )
    for equation, render in zip(missing, rendered):
        db.add_equation(False, equation, settings, render)
    print(f"rendered {len(rendered)} display equations")


@app.command()
def export(output: Path):
    db = Database()

    dir_inline = output / "inline"
    dir_display = output / "display"
    dir_inline.mkdir(exist_ok=True, parents=True)
    dir_display.mkdir(exist_ok=True, parents=True)

    for hash, rendered in db.fetch_rendered_inline():
        with open((dir_inline / hash).with_suffix(".svg"), "w") as fptr:
            fptr.write(rendered)

    for hash, rendered in db.fetch_rendered_display():
        with open((dir_display / hash).with_suffix(".svg"), "w") as fptr:
            fptr.write(rendered)


if __name__ == "__main__":
    app()
