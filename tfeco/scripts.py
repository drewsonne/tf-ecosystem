import click

from tfeco.configuration import ConfigurationFile
from tfeco.workingdirectory import WorkingDirectory

cfg = ConfigurationFile().load().save()


@click.group()
# @click.option('--debug/--no-debug', default=False)
def cli():
    """tf-eco"""
    pass


@cli.command('install-provider')
def install_provider_cmd():
    click.echo('install-provider')


@cli.command('init-stack')
def init_stack_cmd(*args, **kwargs):
    cwd = WorkingDirectory(cfg)
    if not cwd.has_git_ignore():
        cwd.create_git_ignore()

    cwd.create_tf_files(**kwargs)


# Add options from config files
for state, is_optional in cfg.facets():
    if is_optional:
        opt_func = click.option('--' + state, default="")
    else:
        opt_func = click.option('--' + state, required=True)
    init_stack_cmd = opt_func(init_stack_cmd)

if __name__ == '__main__':
    cli(obj={})
