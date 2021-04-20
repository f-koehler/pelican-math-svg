import argparse
import multiprocessing

from .database import Database
from .markdown_extension import render_svg


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs", type=int, default=multiprocessing.cpu_count())
    args = parser.parse_args()

    db = Database()
    missing = db.fetch_missing_equations()

    with multiprocessing.Pool(args.jobs) as pool:
        rendered = pool.map(render_svg, missing)

    print(f"rendered {len(rendered)} equations")

    for equation, render in zip(missing, rendered):
        db.add_equation(equation, render)


if __name__ == "__main__":
    main()
