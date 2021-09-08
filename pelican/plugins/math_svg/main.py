from functools import partial
import multiprocessing

import typer

from pelican import get_instance, parse_arguments

from .database import Database
from .markdown_extension import render_svg
from .settings import PelicanMathSettings

app = typer.Typer()


@app.command()
def run(jobs: int = multiprocessing.cpu_count()):
    pelican, _ = get_instance(parse_arguments([]))
    settings = PelicanMathSettings.from_settings(pelican)

    db = Database()

    missing = db.fetch_missing_inline()
    with multiprocessing.Pool(jobs) as pool:
        rendered = pool.map(
            partial(render_svg, inline=True, settings=settings), missing
        )
    for equation, render in zip(missing, rendered):
        db.add_equation(True, equation, settings, render)
    print(f"rendered {len(rendered)} inline equations")

    missing = db.fetch_missing_inline()
    with multiprocessing.Pool(jobs) as pool:
        rendered = pool.map(
            partial(render_svg, inline=False, settings=settings), missing
        )
    for equation, render in zip(missing, rendered):
        db.add_equation(False, equation, settings, render)
    print(f"rendered {len(rendered)} display equations")


if __name__ == "__main__":
    app()
