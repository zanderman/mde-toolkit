"""MDE Canvas Helper Program.

Automates MDE tasks by interacting with Canvas directly.

This program requires there to be a Canvas API token in a `.env` file.
"""

import click
import logging
import mdetk
import os
from xml.etree import ElementTree

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.option('--input', '-i', required=True, type=click.File(mode='r'), help="Input architecture XML file.")
@click.option('--output', '-o', required=True, type=click.Path(file_okay=False), help="Root path for directories.")
@click.option('--xml-root', required=False, type=str, default='jZPj-5loQ12BBoLkCjAN-1', help="Root node for XML hierarchy.")
@click.option('--dry-run', required=False, type=bool, is_flag=True, help='Show what would be created, without making any directories.')
@click.pass_context
def make_drive_arch(ctx, input, output, xml_root, dry_run):
    """Creates directory hierarchy based on a Draw.io XML file.

    Usage:
        Make directories for architecture 'myarch.drawio.xml' at the current path './'
            $ python mdecli.py make-drive-arch -o ./ -i myarch.drawio.xml

        Custom set XML root element for tree traversal:
            $ python mdecli.py make-drive-arch -o ./ -i myarch.drawio.xml --xml-root "jZPj-5loQ12BBoLkCjAN-1"

        Safely observe output using '--dry-run' option without actually creating anything
            $ python mdecli.py make-drive-arch -o ./ -i myarch.drawio.xml --dry-run
    """
    tree = ElementTree.parse(input)
    graph = mdetk.parse_drive_architecture_xml(tree)
    paths = mdetk.build_directory_structure_from_graph(graph, xml_root)
    for key, path in paths.items():

        # Build directory path.
        newpath = os.path.join(output, path)

        # Make directory.
        print(newpath)
        if not dry_run:
            os.makedirs(newpath)


if __name__ == '__main__':
    cli()