import tkinter as tk


class Node(object):
    """
    # Node
    Represents any particular node in a tree of gui elements.  Specific types
    of Nodes implement this, such as `Frame` and `Label`.
    """

    def __repr__(self):
        value = getattr(self, 'value', None)
        return "<Node({}){}>".format(
            self.__class__.__name__, ' value={}'.format(value) if value else ''
        )

    def __str__(self):
        return getattr(self, 'value', None)

    def __init__(self, parent=None, *args, **kwargs):
        self.nodes = []
        self.depth = 0
        self.pack_data = {}
        self.parent = parent
        if self.parent:
            self.depth = self.parent.depth + 1
            self.parent.nodes.append(self)

    def render(self):
        print('{}{}'.format(('    ' * self.depth), self.__repr__()))
        for node in self.nodes:
            node.build()
            node.render()

    def build(self):
        import ipdb; ipdb.set_trace(); print('wat')
        #build_object = self.build()
        #if isinstance(build_object, Node):
        #    self._object = build_object._object
        #else:
        #    self._object = build_object
        #self._object = self.build()

    def show(self):
        self._object.pack(self.pack_data)

    def hide(self):
        self._object.pack_forget()


class Gui(Node):
    def __init__(self, parent=None, title: str = None, binds=None):
        self.title = title
        self.binds = binds
        super().__init__(parent=parent)

    def build(self):
        obj = tk.Tk()
        obj.title(self.title)
        return obj

    def render(self):
        super().render()
        self._object.mainloop()

    def quit(self):
        self._object.quit()

    def bind(self, a, b):
        self._object.bind(a, b)


class Window(Node):
    def __init__(self, width=None, height=None, parent=None):
        self.width = width
        self.height = height
        super().__init__(parent=parent)

    def build(self):
        return Frame(parent=self.parent, width=self.width, height=self.height)

    def render(self):
        super().render()


class Frame(Node):
    def __init__(self, width=None, height=None, parent=None):
        self.width = width
        self.height = height
        super().__init__(parent=parent)

    def build(self):
        return tk.Frame(
            self.parent._object, width=self.width, height=self.height, bd=2
        )

    def render(self):
        self._object.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5)
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
            anchor=self.anchor
        )
        self._object.pack(side=tk.LEFT)
        super().render()


class Entry(Node):
    def __init__(self, value=None, parent=None):
        self.value = value
        super().__init__(parent=parent)

    @property
    def text(self):
        return self._object.get()

    def build(self):
        value = tk.StringVar()
        value.set(self.value)
        return tk.Entry(self.parent._object, textvariable=value)

    def render(self):
        self._object.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
        super().render()


class Button(Node):
    def __init__(
        self,
        text: str,
        parent=None,
        command=None,
        side: str = None,
        pad: int = None
    ):
        super().__init__(parent=parent)
        self.text = text
        self.command = command
        self.side = side or tk.LEFT
        self.pad = pad or 5

    def render(self):
        self._object = tk.Button(
            self.parent._object, text=self.text, command=self.command
        )
        self._object.pack(side=self.side, padx=self.pad, pady=self.pad)
        super().render()


class Form(Node):
    def __init__(self, data: dict, parent: str = None):
        super().__init__(parent=parent)
        self.frame = Frame(parent=parent)
        _, __, entries = self.build(data, parent=self.frame)
        self.entries = entries

    def build(self, data=None, parent=None, agg=None):
        entry = None
        agg = agg or []

        if isinstance(data, dict):
            for field, value in data.items():
                row = Frame(parent=parent)
                dentry, dparent, agg = self.build(value, parent=row, agg=agg)
                lab = Label(text=field, parent=row)
                #agg.append((field, dentry))
        elif isinstance(data, list):
            for field in data:
                nentry, parent, agg = self.build(field, parent=parent, agg=agg)
        else:
            entry = Entry(value=data, parent=parent)
            agg.append(entry)
        return entry, parent, agg

    def fetch(self, ent):
        data = {}
        for entry in self.entries:
            field = entry[0]
            text = entry[1].text
            data[field] = text
            import ipdb
            ipdb.set_trace()
            print('wat')
        return data


class Listbox(Node):
    def __init__(self, values: list = None, parent=None):
        super().__init__(parent=parent)
        self.values = values or []

    def build(self):
        node = tk.Listbox(self.parent._object)
        for value in self.values:
            node.insert(tk.END, value)
        return node

    def render(self):
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


class Panes(Node):
    def __init__(self, panes, parent=None):
        super().__init__(parent=parent)
        self.panes = panes

    def render(self):
        self._object = tk.PanedWindow(self.parent._object)
        self._object.pack(fill=tk.BOTH, expand=1)
        for pane in self.panes:
            self._object.add(pane)


class Menu(Node):
    def __init__(self, commands, parent=None):
        super().__init__(parent=parent)
        if not commands:
            commands = []
        self.commands = commands

    def build(self):
        menu = tk.Menu(self.parent._object)
        for command in self.commands:
            menu.add_command(label='Wat', command=None)

    def render(self):
        pass


class View(Node):
    pass


# a base tab class
class Tab(Node):
    def __init__(self, name: str, parent=None):
        self.name = name
        super().__init__(parent=parent)

    def build(self):
        args = []
        if self.parent:
            args.append(self.parent._object)
        return tk.Frame(*args)

    def show(self):
        self._object.pack(side=tk.BOTTOM)


# the bulk of the logic is in the actual tab bar
class TabBar(Node):
    def __init__(self, name: str = None, tabs: list = None, parent=None):
        self.tabs = {}
        self.buttons = {}
        self.current_tab = None
        self.name = name
        super().__init__(parent=parent)

    def build(self):
        tab_bar = tk.Frame(self.parent._object)
        if self.tabs:
            for tab in tabs:
                pass    #self.add(tab)
        return tab_bar

    def render(self):
        self.show()
        super().render()

    def show(self):
        self._object.pack(side=tk.TOP, expand=tk.YES, fill=tk.X)
        keys = [k for k in self.tabs.keys()]
        if keys:
            self.switch_tab(keys[0])

    @classmethod
    def _add(cls, tab):
        pass

    def add(self, tab):
        tab.hide()
        self.tabs[tab.name] = tab
        cmd = (lambda name=tab.name: self.switch_tab(name))
        b = tk.Button(
            self._object, text=tab.name, relief=tk.RAISED, command=cmd
        )
        b.pack(side=tk.LEFT)
        self.buttons[tab.name] = b

    def delete(self, tabname):
        if tabname == self.current_tab:
            self.current_tab = None
            self.tabs[tabname].hide()
            del self.tabs[tabname]
            self.switch_tab(self.tabs.keys()[0])

        else:
            del self.tabs[tabname]

        self.buttons[tabname].hide()
        del self.buttons[tabname]

    def switch_tab(self, name):
        print('SWITCHING TAB {}'.format(name))
        if self.current_tab:
            self.buttons[self.current_tab].config(relief=tk.RAISED)
            self.tabs[self.current_tab].hide()
        self.tabs[name].show()
        self.current_tab = name
        self.buttons[name].config(relief=tk.FLAT)
