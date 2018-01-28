import tkinter as tk


class Node(object):
    def __init__(self, parent=None, *args, **kwargs):
        self.nodes = []
        self.parent = parent
        if self.parent:
            self.parent.nodes.append(self)

    def render(self):
        for node in self.nodes:
            node.render()


class Window(Node):
    def __init__(self, parent=None, title: str = None, binds=None):
        super().__init__(parent=parent)
        self.title = title

    def render(self):
        self._object = tk.Tk()
        self._object.title(self.title)
        super().render()
        self._object.mainloop()

    def quit(self):
        self._object.quit()

    def bind(self, a, b):
        self._object.bind(a, b)


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
    def __init__(self, fields: dict, parent: str = None):
        super().__init__(parent=parent)
        self.frame = Frame(parent=parent)
        self.entries = []
        for field, value in fields.items():
            row = Frame(parent=self.frame)
            lab = Label(text=field, parent=row)
            ent = Entry(value=value, parent=row)
            self.entries.append((field, ent))

    def fetch(self, ent):
        data = {}
        for entry in self.entries:
            field = entry[0]
            text = entry[1].text
            data[field] = text
        return data


class ActionBar(Node):
    def __init__(self):
        pass
