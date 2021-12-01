"""tftf - terraform transformation"""

import json
import logging
import subprocess

import click

from tftf.transform import Transform

logger = logging.getLogger(__name__)


@click.command()
@click.argument("action")
@click.option("--plan", "-p", type=click.File("rb"), help="plan.out in json format")
@click.option(
    "--transformations",
    "-t",
    type=click.File("rb"),
    help="transformations in json format",
)
def cli(action, plan, transformations):
    """tftf - terraform state transformation

    ACTION is either plan or apply to show the tfstate migrations that would be applied or actually apply them
    """
    click.echo(f"action is {action}")
    plan_dict = json.load(plan)
    transformations_dict = json.load(transformations)

    moves = Transform(plan_dict, transformations_dict)

    if len(tuple(moves)) == 0:
        click.echo("tftf: no resources found matching transformations")
        exit(0)

    cmds = []
    for m in moves:
        # we create the steps in a subprocess friendly list of lists
        cmds.append(["terraform", "state", "mv", m.get("src"), m.get("dst")])

    if action == "apply":
        for cmd in cmds:
            click.echo("Executing `{}`".format(" ".join(cmd)))
            subprocess.run(cmd)
    elif action == "plan":
        click.echo("tftf will performe the following actions:")
        for cmd in cmds:
            click.echo(" ".join(cmd))
    else:
        logger.error("Unknown action {action}")
        exit(1)


if __name__ == "__main__":
    cli()
