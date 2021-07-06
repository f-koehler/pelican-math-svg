import argparse
from functools import partial
import multiprocessing

from pelican import get_instance, parse_arguments

from .database import Database
from .markdown_extension import render_svg
from .settings import PelicanMathSettings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, default=multiprocessing.cpu_count())
    args = parser.parse_args()

    pelican, _ = get_instance(parse_arguments([]))
    settings = PelicanMathSettings.from_settings(pelican)

    db = Database()
    missing = db.fetch_missing_equations()

    with multiprocessing.Pool(args.jobs) as pool:
        rendered = pool.map(partial(render_svg, settings=settings), missing)

    print(f"rendered {len(rendered)} equations")

    for equation, render in zip(missing, rendered):
        db.add_equation(equation, settings, render)


if __name__ == "__main__":
    main()
