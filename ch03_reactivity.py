import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell
def _(channel, channel_data, mo):
    # Эта ячейка стоит выше тех, от которых зависит, -- marimo всё равно
    # выполнит её последней: порядок задаёт граф, а не место на странице.
    n_anomalies = channel_data["is_anomaly"].sum()
    mo.md(
        f"Канал **{channel}**. Число измерений: {channel_data.height}, "
        f"из них аномалий: {n_anomalies}."
    )
    return


@app.cell
def _():
    channel = "P-1"  # замените на "C-1" -- ячейки ниже пересчитаются сами
    return (channel,)


@app.cell
def _(mo, pl):
    telemetry = pl.read_parquet(mo.notebook_dir() / "data" / "telemetry.parquet")
    return (telemetry,)


@app.cell
def _(channel, pl, telemetry):
    channel_data = telemetry.filter(
        (pl.col("chan_id") == channel) & (pl.col("split") == "test")
    )
    return (channel_data,)


if __name__ == "__main__":
    app.run()
