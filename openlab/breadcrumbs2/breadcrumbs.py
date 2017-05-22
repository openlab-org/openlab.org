class TabSet(set):
    def __getitem__(self, s):
        return s in self

class Breadcrumbs(dict):
    def __init__(self):
        self.list = []

    def append(self, *args, name=None):
        """
        Example:
        request.breadcrumbs.append("Project", , name="toptab")
        """
        if name:
            if name not in self:
                self[name] = TabSet()
            val = args[0].replace(" ", "_").lower().strip()
            self[name].add(args[0].lower())

        return self.list.append(args)

    def extend(self, other):
        self.list.extend(other.list)
        self.update(other)

