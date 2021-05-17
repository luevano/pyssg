import os


# db class that works for both html and md files
class Database:
    def __init__(self, db_path: str):
        self.db_path: str = db_path
        self.e: dict[str, tuple[float, float, list[str]]] = dict()


    # updates the tags for a specific entry (file)
    def update_tags(self, file_name: str,
                    tags: list[str]) -> None:
        if file_name in self.e:
            cts, mts, _ = self.e[file_name]
            self.e[file_name] = (cts, mts, tags)


    # returns a bool that indicates if the entry
    # was (includes new entries) or wasn't updated
    # 0.0 means no mod
    def update(self, file_name: str,
               remove: str=None) -> bool:
        # initial default values
        f: str = file_name
        tags: list[str] = []
        if remove is not None:
            f = file_name.replace(remove, '')


        # get current time, needs actual file name
        time: float = os.stat(file_name).st_mtime

        # three cases, 1) entry didn't exist,
        # 2) entry hasn't been mod and,
        # 3) entry has been mod
        #1)
        if f not in self.e:
            self.e[f] = (time, 0.0, tags)
            return True

        old_time, old_mod_time, tags = self.e[f]

        # 2)
        if old_mod_time == 0.0:
            if time > old_time:
                self.e[f] = (old_time, time, tags)
                return True
        # 3)
        else:
            if time > old_mod_time:
                self.e[f] = (old_time, time, tags)
                return True

        return False


    def write(self) -> None:
        with open(self.db_path, 'w') as file:
            # write each k,v pair in dict to db file
            for k, v in self.e.items():
                t: str = None
                if len(v[2]) == 0:
                    t = '-'
                else:
                    t = ','.join(v[2])
                file.write(f'{k} {v[0]} {v[1]} {t}\n')


    def read(self) -> None:
        # only if the path exists and it is a file
        if os.path.exists(self.db_path) and os.path.isfile(self.db_path):
            # get all db file lines
            lines: list[str] = None
            with open(self.db_path, 'r') as file:
                lines = file.readlines()

            # parse each entry and populate accordingly
            l: list[str] = None
            # l=list of values in entry
            for line in lines:
                l = tuple(line.strip().split())
                if len(l) != 4:
                    raise Exception('db entry doesn\'t contain 4 elements')

                t: list[str] = None
                if l[3] == '-':
                    t = []
                else:
                    t = l[3].split(',')

                self.e[l[0]] = (float(l[1]), float(l[2]), t)
