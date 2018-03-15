from importlib import import_module


def import_from_string(val: str, setting_name: str):
    try:
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = import_module(module_path)

        return getattr(module, class_name)

    except (ImportError, AttributeError) as e:
        msg = f'Unable to import {val} for {setting_name}. {e.__class__.__name__}: {e}.'

        raise ImportError(msg)


def transform_header_to_django_meta_format(header: str) -> str:
    header = header.upper()
    header = header.replace('-', '_')

    return f'HTTP_{header}'
