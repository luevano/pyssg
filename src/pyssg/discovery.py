import os


def get_file_list(directory: str,
                  extensions: list[str],
                  exclude: list[str]=None) -> list[str]:
    out: list[str] = []
    for root, dirs, files in os.walk(directory):
        if exclude is not None:
            dirs[:] = [d for d in dirs if d not in exclude]

        for f in files:
            if f.endswith(tuple(extensions)):
                out.append(os.path.join(root, f).replace(directory, '')[1:])

    return out


def get_dir_structure(directory: str,
                      exclude: list[str]=None) -> list[str]:
    out: list[str] = []
    for root, dirs, files in os.walk(directory):
        if exclude is not None:
            dirs[:] = [d for d in dirs if d not in exclude]

        for d in dirs:
            if root in out:
                out.remove(root)
                out.append(os.path.join(root, d))

    return [o.replace(directory, '')[1:] for o in out]
