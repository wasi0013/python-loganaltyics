"""Console script for py_logan."""
import sys
import click
from py_logan.nginx.audit import generate_csv_reports

@click.command()
@click.option('--server', default="nginx", help='Name of the web server')
@click.option('--log',  help="Web server's log directory.")
def audit(server,  log):
    if server == 'nginx':
        generate_csv_reports(log)    
    
    return 0


if __name__ == "__main__":
    sys.exit(audit())  # pragma: no cover
