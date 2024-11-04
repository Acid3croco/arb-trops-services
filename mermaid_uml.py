import inspect
import argparse

from pathlib import Path
from types import FunctionType
from argparse import ArgumentParser
from importlib.machinery import SourceFileLoader

import ccxt

from arb_logger.logger import get_logger

SCRIPT_NAME = Path(__file__).stem
LOGGER = get_logger(SCRIPT_NAME, log_in_file=False)
DEFAULT_SAVE_PATH = 'README.uml.md'


class MermaidUMLGenerator:

    def __init__(self, root_path, exclude, module_only):
        self.root_path: list[Path] = root_path
        self.excludes: list[Path] = exclude or []
        self.module_only = module_only

        self.diagram = []

    def _get_all_files(self):
        return [
            p.glob('**/*.py') if not p.is_file() else [p]
            for p in self.root_path
        ]

    def _exclude_files(self, file):
        default_excludes = ['__init__.py', 'setup.py']

        if file.name in default_excludes:
            return True

        for p in self.root_path:
            if p.is_file():
                continue

            if self.module_only:
                if p.absolute() not in [d.absolute() for d in file.parents]:
                    return True

            for exclude in self.excludes:

                if exclude.is_dir() or (p / exclude).is_dir():
                    exclude = exclude if exclude.exists() else p / exclude
                    if exclude in file.parents:
                        return True
                elif exclude == file or p / exclude == file:
                    return True

    def _load_module(self, module_path: Path):
        module_name = module_path.stem
        LOGGER.info(f'Loading module {module_name} from {module_path}...')
        try:
            module = SourceFileLoader(module_name, str(
                module_path.absolute())).load_module()
            LOGGER.info(f'Loaded module {module_name} from {module_path}')
            return module
        except ModuleNotFoundError as e:
            LOGGER.error(
                f'Failed to load module {module_name} from {module_path}: {e}')

    def _is_valid_file(self, file_path):
        return file_path.is_file() and file_path.suffix == '.py'

    def _skip_ccxt(self, name, cls):
        if name == 'poloniexfutures':
            return True
        if name in ccxt.exchanges:
            return True
        if cls.__module__ == 'ccxt':
            return True

    def _skip_models(self, name, cls):
        if name == 'BaseModel':
            return True
        if name.endswith('Model'):
            return True
        if cls.__module__ == 'db_handler.models':
            return True

    def _skip_class(self, name, cls):
        return any([
            self._skip_ccxt(name, cls),
            self._skip_models(name, cls),
        ])

    def _check_parents(self, name, cls):
        for pcls in cls.__bases__:
            if pcls not in [object]:
                self.diagram.append(f'{pcls.__name__} <|-- {name}')

    def _add_method(self, name, meth, meth_call):
        if meth.startswith(f'_{name}__'):
            # clean __ private method class prefix
            meth = meth.replace(f'_{name}__', '__')

        prefix = '+'
        if meth.startswith('_'):
            prefix = '-'
        signature = inspect.signature(meth_call)
        self.diagram.append(
            f'\t{prefix}{meth}{signature if len(str(signature)) < 100 else ""}'
        )

    def _add_attribute(self, attribute):
        prefix = '+'
        if attribute.startswith('_'):
            prefix = '-'
        self.diagram.append(f'\t{prefix}{attribute}')

    def _inspect_dataclass(self, name, cls):
        LOGGER.info(f'Inspecting dataclass {name}...')
        self.diagram.append(f'class {name} {{')
        for field in cls.__dict__['__dataclass_fields__'].values():
            try:
                attribute = f'{field.type.__name__} {field.name}'
            except AttributeError:
                attribute = f'{field.type} {field.name}'
            self._add_attribute(attribute)
        self.diagram.append('}')

    def _inspect_class(self, name, cls):
        LOGGER.info(f'Inspecting class {name}...')
        self.diagram.append(f'class {name} {{')

        for member in dir(cls):
            member_call = getattr(cls, member)
            if isinstance(member_call,
                          (FunctionType, classmethod, staticmethod)):
                if not member_call.__qualname__.startswith(name):
                    # skip inherited methods
                    continue
                self._add_method(name, member, member_call)
            elif not (member.startswith('__')
                      and member.endswith('__')) and member not in [
                          '_abc_impl', '__dataclass_fields__'
                      ]:
                self._add_attribute(member)

        self.diagram.append('}')

    def build(self):
        all_files = self._get_all_files()

        for sub_files in all_files:
            for file in sub_files:
                if not self._is_valid_file(file):
                    continue
                if self._exclude_files(file):
                    LOGGER.info(f'Excluding file {file}')
                    continue

                module_name = file.stem
                module = self._load_module(file)
                for name, cls in inspect.getmembers(module, inspect.isclass):
                    if cls.__module__ != module_name:
                        # skip inherited classes
                        continue

                    self._check_parents(name, cls)
                    if self._skip_class(name, cls):
                        continue
                    if '__dataclass_fields__' in cls.__dict__:
                        self._inspect_dataclass(name, cls)
                    else:
                        self._inspect_class(name, cls)

        if not self.diagram:
            LOGGER.error('No classes found')
            exit(1)

    def _get_diagram_str(self):
        diagram = ['classDiagram'] + [f'\t{l}' for l in self.diagram]
        return '\n'.join(diagram)

    def show(self):
        diagram = self._get_diagram_str()
        LOGGER.info(f'\n\n{diagram}\n\n')

    def save(self, path):
        diagram = self._get_diagram_str()
        with open(path, 'w') as f:
            f.write('# UML Diagram\n\n')
            f.write('```mermaid\n')
            f.write(diagram)
            f.write('\n```\n')


def valid_path(path):
    try:
        return Path(path)
    except Exception as e:
        raise argparse.ArgumentTypeError(f'Invalid path: {path} ({e})') from e


def main():
    parser = ArgumentParser(
        description='Generate UML diagram from Python classes')
    parser.add_argument('-p',
                        '--path',
                        type=valid_path,
                        help='Paths to Python file or directory',
                        nargs='+',
                        default=[Path('./')])
    parser.add_argument(
        '-s',
        '--save',
        nargs='?',
        metavar='PATH',
        help=f'Save diagram to file, default to {DEFAULT_SAVE_PATH}',
        default=argparse.SUPPRESS)
    parser.add_argument('-e',
                        '--exclude',
                        nargs='*',
                        type=valid_path,
                        help='Exclude files from diagram generation')
    parser.add_argument('-m',
                        '--module',
                        help='Only map module methods',
                        action='store_true')

    args = parser.parse_args()

    mermaid = MermaidUMLGenerator(args.path, args.exclude, args.module)
    mermaid.build()
    if 'save' in args:
        mermaid.save(args.save or DEFAULT_SAVE_PATH)
    else:
        mermaid.show()


if __name__ == '__main__':
    main()
