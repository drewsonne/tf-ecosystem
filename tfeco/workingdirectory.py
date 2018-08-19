import os
from pathlib import Path


class WorkingDirectory(object):
    def __init__(self, cfg):
        self._cfg = cfg

        self._cwd = Path(os.getcwd())

        self._gitignore = self._cwd / ".gitignore"
        self._tf_config = self._cwd / "_eco_override.tf"

        self._terraform_folder = self._cwd / ".terraform"
        self._tf_environment = self._terraform_folder / "environment"

    def has_git_ignore(self):
        return self._gitignore.exists() and \
               self._gitignore.is_file()

    def create_git_ignore(self):
        with self._gitignore.open('w') as fp:
            fp.write("""_*tf
_*tfvars
""")

    def has_tf_files(self):
        return self._tf_config.exists() and \
               self._tf_config.is_file()

    def create_tf_files(self, **cli_args):

        composer = self._cfg.composer(**cli_args)

        if self._tf_config.exists():
            self._tf_config.chmod(0o666)

        with self._tf_config.open('w') as fp:
            composer.compose(fp)
        self._tf_config.chmod(0o444)

        if not self._terraform_folder.exists():
            self._terraform_folder.mkdir(0o777)

        with self._tf_environment.open('w') as fp:
            composer.compose_env(fp)

        if self._tf_environment.exists():
            self._tf_environment.chmod(0o666)
