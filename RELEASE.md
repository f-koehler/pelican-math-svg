Release type: minor

Add settings to rescale inline and display math. Also redesign database to achieve this.

**Warning:** due to the change of the database format, it is necessary to delete the database located at `.cache/pelican-math-svg/equations.db`. This will also trigger a rebuild of all equations.
