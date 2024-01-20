import click
import uvicorn


@click.group()
def cli() -> None:
    """
    CLI For real
    """
    pass


@cli.command(help="Run server")
@click.option("-h", "--host", default="0.0.0.0", help="Host")
@click.option("-p", "--port", type=click.INT, default=8000, help="Port")
def run_server(host: str, port: int) -> None:
    uvicorn.run("app.main:app", host=host, port=port, reload=True)


if __name__ == "__main__":
    cli()
