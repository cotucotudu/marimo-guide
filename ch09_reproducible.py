# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "marimo",
#     "polars==2.0.0",
# ]
# ///

import marimo

__generated_with = "0.25.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import polars as pl

    return mo, pl


@app.cell
def _(mo):
    channel = mo.cli_args().get("channel", "P-1")
    return (channel,)


@app.cell
def _(channel, mo, pl):
    data = pl.read_parquet(mo.notebook_dir() / "data" / "telemetry.parquet").filter(
        (pl.col("chan_id") == channel) & (pl.col("split") == "test")
    )
    n_anomalies = data["is_anomaly"].sum()
    print(f"Канал {channel}. Число измерений: {data.height}, из них аномалий: {n_anomalies}")
    return


if __name__ == "__main__":
    app.run()
