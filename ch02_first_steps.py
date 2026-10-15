import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Телеметрия SMAP и MSL

    Первый ноутбук marimo: загружаем данные и смотрим на них.
    """)
    return


@app.cell
def _(mo, pl):
    telemetry = pl.read_parquet(mo.notebook_dir() / "data" / "telemetry.parquet")
    telemetry
    return (telemetry,)


@app.cell
def _(mo, telemetry):
    n_channels = telemetry["chan_id"].n_unique()
    n_rows = telemetry.height
    mo.md(f"Число каналов: **{n_channels}**, число измерений: **{n_rows}**.")
    return


if __name__ == "__main__":
    app.run()
