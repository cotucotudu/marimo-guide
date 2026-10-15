import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell
def _(mo, pl):
    telemetry = pl.read_parquet(mo.notebook_dir() / "data" / "telemetry.parquet")
    anomalies = pl.read_csv(mo.notebook_dir() / "data" / "anomalies.csv")
    return anomalies, telemetry


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Датафрейм как результат ячейки
    """)
    return


@app.cell
def _(telemetry):
    telemetry
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Таблица с выбором строк
    """)
    return


@app.cell
def _(anomalies, mo):
    anomaly_table = mo.ui.table(
        anomalies,
        selection="single",
        initial_selection=[0],
        label="Выберите аномалию",
    )
    anomaly_table
    return (anomaly_table,)


@app.cell
def _(anomaly_table, mo, pl, telemetry):
    selected = anomaly_table.value
    mo.stop(selected.is_empty(), mo.md("*Выберите строку в таблице.*"))

    chan, start, end = selected.select("chan_id", "start", "end").row(0)
    window = telemetry.filter(
        (pl.col("chan_id") == chan)
        & (pl.col("split") == "test")
        & pl.col("step").is_between(start - 100, end + 100)
    )
    mo.vstack([
        mo.md(f"Канал **{chan}**, шаги {start}–{end}; число измерений: {window.height}"),
        window,
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Преобразования без кода
    """)
    return


@app.cell
def _(mo, telemetry):
    transformer = mo.ui.dataframe(telemetry)
    transformer
    return (transformer,)


@app.cell
def _(mo, transformer):
    mo.md(f"После преобразований осталось **{transformer.value.height}** строк.")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Обзор данных
    """)
    return


@app.cell
def _(mo, pl, telemetry):
    mo.ui.data_explorer(
        telemetry.filter(pl.col("chan_id") == "P-1"),
        x="step", y="value", color="is_anomaly",
    )
    return


if __name__ == "__main__":
    app.run()
