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
    ## 1. Загрузка файла
    """)
    return


@app.cell
def _(mo):
    upload = mo.ui.file(filetypes=[".csv"], label="Загрузите файл канала (CSV)")
    upload
    return (upload,)


@app.cell
def _(mo, pl, upload):
    mo.stop(not upload.value, mo.md("*Файл ещё не загружен.*"))
    channel = pl.read_csv(upload.contents())
    mo.md(f"Файл **{upload.name()}**, число строк: {channel.height}.")
    return (channel,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. SQL-запрос к датафрейму
    """)
    return


@app.cell
def _(mo, pl):
    anomalies = pl.read_csv(mo.notebook_dir() / "data" / "anomalies.csv")
    return (anomalies,)


@app.cell
def _(anomalies, mo):
    summary = mo.sql(
        f"""
        SELECT spacecraft, class,
               COUNT(*) AS n_anomalies,
               SUM("end" - start + 1)::INTEGER AS n_steps
        FROM anomalies
        GROUP BY spacecraft, class
        ORDER BY spacecraft, class
        """
    )
    return (summary,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Кэширование
    """)
    return


@app.cell
def _(mo, pl):
    with mo.persistent_cache(name="telemetry"):
        telemetry = pl.read_parquet(mo.notebook_dir() / "data" / "telemetry.parquet")
    return (telemetry,)


@app.cell
def _(mo, pl, telemetry):
    stats = telemetry.group_by("chan_id").agg(
        pl.col("value").mean().alias("mean"),
        pl.col("value").std().alias("std"),
    ).sort("chan_id")
    stats
    return (stats,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 4. Выгрузка результата
    """)
    return


@app.cell
def _(mo, stats):
    mo.download(
        data=lambda: stats.write_csv().encode("utf-8"),
        filename="channel_stats.csv",
        label="Скачать статистику (CSV)",
    )
    return


if __name__ == "__main__":
    app.run()
