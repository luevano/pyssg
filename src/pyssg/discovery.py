import os


def get_file_list(extensions: list[str], exclude: list[str]=None) -> list[str]:
    cwd = os.getcwd()

    out = []
    for root, dirs, files in os.walk(cwd):
        if exclude is not None:
            dirs[:] = [d for d in dirs if d not in exclude]

        for f in files:
            if f.endswith(tuple(extensions)):
                out.append(os.path.join(root, f).replace(cwd, '')[1:])

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
            out.append(os.path.join(root, d))

    return [o.replace(cwd, '')[1:] for o in out]


def get_all_files(src: str) -> tuple[list[str], list[str], list[str]]:
    iwd = os.getcwd()
    os.chdir(src)

    md_files = get_file_list(['.md', '.markdown'], ['templates'])
    html_files = get_file_list(['.html'], ['templates'])
    dirs = get_dir_structure(['templates'])

    os.chdir(iwd)

    return (dirs, md_files, html_files)
