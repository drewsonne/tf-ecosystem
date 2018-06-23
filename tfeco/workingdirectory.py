import os
from pathlib import Path


class WorkingDirectory(object):
    def __init__(self, cfg):
        self._cfg = cfg

        self._cwd = Path(os.getcwd())

        self._gitignore = self._cwd / ".gitignore"
        self._tf_config = self._cwd / "_eco_override.tf"

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
        if self._tf_config.exists():
            self._tf_config.chmod(0o666)
        with self._tf_config.open('w') as fp:
            composer = self._cfg.composer(**cli_args)
            composer.compose(fp)
        self._tf_config.chmod(0o444)
