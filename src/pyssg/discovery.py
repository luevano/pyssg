import os


def get_file_list(extensions: list[str], exclude: list[str]=None) -> list[str]:
    cwd = os.getcwd()

    out = []
    for root, dirs, files in os.walk(cwd):
        if exclude is not None:
            dirs[:] = [d for d in dirs if d not in exclude]

        for f in files:
            if f.endswith(tuple(extensions)):
                out.append(os.path.join(root, f))

    return out


def get_dir_structure(exclude: list[str]=None) -> list[str]:
    cwd = os.getcwd()

    out = []
    for root, dirs, files in os.walk(cwd):
        if exclude is not None:
            dirs[:] = [d for d in dirs if d not in exclude]

        for d in dirs:
            if root in out:
                out.remove(root)
            out.append(os.path.join(root, d).replace(cwd, ''))

    return out


def get_all_files():
    md_files = get_file_list(['.md', '.markdown'], ['templates'])
    html_files = get_file_list(['.html'], ['templates'])
    dirs = get_dir_structure(['templates'])

    return (dirs, md_files, html_files)
