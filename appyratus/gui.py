import tkinter as tk


class Node(object):
    def __repr__(self):
        value = getattr(self, 'value', None)
        parent = self.parent
        return "<Node({})/value={}>".format(self.__class__.__name__, value)

    def __str__(self):
        return getattr(self, 'value', None)

    def __init__(self, parent=None, *args, **kwargs):
        self.nodes = []
        self.parent = parent
        if self.parent:
            self.parent.nodes.append(self)

    @property
    def object(self):
        if not self._object:
            import ipdb
            ipdb.set_trace()
        return self._object

    def render(self):
        for node in self.nodes:
            node.render()


class Gui(Node):
    def __init__(self, parent=None, title: str = None, binds=None):
        super().__init__(parent=parent)
        self.title = title
        self.binds = binds

    def render(self):
        self._object = tk.Tk()
        self._object.title(self.title)
        super().render()
        self._object.mainloop()

    def quit(self):
        self._object.quit()

    def bind(self, a, b):
        self._object.bind(a, b)


class Window(Node):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def render(self):
        self._object = tk.Frame(self.parent._object)
        super().render()


class Frame(Node):
    def render(self):
        self._object = tk.Frame(self.parent._object)
        self._object.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        super().render()


class Label(Node):
    def __init__(self, text: str, parent=None):
        super().__init__(text=text, parent=parent)
        self.text = text
        self.parent = parent
        self.width = '15'
        self.anchor = 'w'

    def render(self):
        self._object = tk.Label(
            self.parent._object,
            width=self.width,
            text=self.text,
            anchor=self.anchor)
        self._object.pack(side=tk.LEFT)
        super().render()


class Entry(Node):
    def __init__(self, value=None, parent=None):
        super().__init__(parent=parent)
        self.value = value

    @property
    def text(self):
        return self._object.get()

    def render(self):
        value = tk.StringVar()
        value.set(self.value)
        self._object = tk.Entry(self.parent._object, textvariable=value)
        self._object.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        super().render()


class Button(Node):
    def __init__(self,
                 text: str,
                 parent=None,
                 command=None,
                 side: str = None,
                 pad: int = None):
        super().__init__(parent=parent)
        self.text = text
        self.command = command
        self.side = side or tk.LEFT
        self.pad = pad or 5

    def render(self):
        self._object = tk.Button(
            self.parent._object, text=self.text, command=self.command)
        self._object.pack(side=self.side, padx=self.pad, pady=self.pad)
        super().render()


class Form(Node):
    def __init__(self, data: dict, parent: str = None):
        super().__init__(parent=parent)
        self.frame = Frame(parent=parent)
        self.entries = self.build(data, parent=self.frame)

        import ipdb
        ipdb.set_trace()
        pass

    def build(self, data=None, parent=None, agg=None):
        entry = None
        agg = agg or {}
        if 'entries' not in agg:
            agg['entries'] = []

        if isinstance(data, dict):
            for field, value in data.items():
                row = Frame(parent=parent)
                dentry, dparent, agg = self.build(value, parent=row, agg=agg)
                lab = Label(text=field, parent=row)
                agg['entries'].append((field, dentry))
        elif isinstance(data, list):
            for field in data:
                nentry, parent, agg = self.build(field, parent=parent, agg=agg)
        else:
            entry = Entry(value=data, parent=parent)
            agg['entries'].append(entry)
        return entry, parent, agg

    def fetch(self, ent):
        data = {}
        for entry in self.entries:
            field = entry[0]
            text = entry[1].text
            data[field] = text
        return data


class Listbox(Node):
    def __init__(self, values: list = None, parent=None):
        super().__init__(parent=parent)
        self.values = values or []

    def build(self):
        pass

    def render(self):
        self._object = tk.Listbox(self.parent._object)
        for value in self.values:
            self.add(value)
        self._object.pack()

    def clear(self):
        self._object.delete(0, tk.END)

    def add(self, value):
        self._object.insert(tk.END, value)


class Scrollbar(Node):
    def render(self):
        scrollbar = tk.Scrollbar(self.parent._object)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


class ControlBar(Node):
    def __init__(self, buttons, parent=None):
        super().__init__(parent=parent)
        self.buttons = buttons

    def render(self):
        super().render()


class View(Node):
    pass
