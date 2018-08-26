import tkinter as tk


class Node(object):
    """
    # Node
    Represents any particular node in a tree of gui elements.  Specific types
    of Nodes implement this, such as `Frame` and `Label`.
    """

    def __repr__(self):
        value = getattr(self, 'value', None)
        value_str = str(value)[0:32] if value else value
        return "<Node({}){}>".format(
            self.__class__.__name__, ' value={}/"{}"'.format(value.__class__.__name__, value_str) if value else ''
        )

    def __str__(self):
        return getattr(self, 'value', '')

    def __init__(self, parent=None, *args, **kwargs):
        self.nodes = []
        self.depth = 0
        self.pack_data = {}
        self.parent = parent
        if self.parent:
            self.depth = self.parent.depth + 1
            self.parent.nodes.append(self)

    def build(self):
        print('{} {} ({})'.format('  ' * self.depth, repr(self), len(self.nodes)))
        self._object = self.build_object()
        self.build_children()

    def build_children(self):
        for node in self.nodes:
            node.build()

    def render(self):
        print('{} {} ({})'.format('  ' * self.depth, repr(self), len(self.nodes)))
        self.render_children()
        self.render_object()

    def render_children(self):
        for node in self.nodes:
            node.render()

    def render_object(self):
        self._object.pack(self.pack_data)

    def hide(self):
        self._object.pack_forget()


class Gui(Node):
    """
    # Gui
    Top-most node
    """

    def __init__(self, parent=None, title: str=None, binds=None):
        self.title = title
        self.binds = binds
        super().__init__(parent=parent)

    def build_object(self):
        obj = tk.Tk()
        obj.title(self.title)
        return obj

    def render_object(self):
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

    def build_object(self):
        return Frame(parent=self.parent, width=self.width, height=self.height)

    def render_object(self):
        pass


class Frame(Node):
    def __init__(self, width=None, height=None, parent=None):
        self.width = width
        self.height = height
        super().__init__(parent=parent)

    def build_object(self):
        return tk.Frame(
            self.parent._object, width=self.width, height=self.height, bd=2
        )

    def render_object(self):
        self._object.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5)


class Label(Node):
    def __init__(self, text: str, parent=None):
        super().__init__(text=text, parent=parent)
        self.text = text
        self.parent = parent
        self.width = '15'
        self.anchor = 'w'

    def build_object(self):
        return tk.Label(
            self.parent._object,
            width=self.width,
            text=self.text,
            anchor=self.anchor
        )

    def render_object(self):
        self._object.pack(side=tk.LEFT)


class Entry(Node):
    def __init__(self, value=None, parent=None):
        self.value = value
        super().__init__(parent=parent)

    @property
    def text(self):
        return self._object.get()

    def build_object(self):
        value = tk.StringVar()
        value.set(self.value)
        return tk.Entry(self.parent._object, textvariable=value)

    def render_object(self):
        self._object.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)


class Button(Node):
    def __init__(
        self,
        text: str,
        parent=None,
        command=None,
        side: str=None,
        pad: int=None
    ):
        super().__init__(parent=parent)
        self.text = text
        self.command = command
        self.side = side or tk.LEFT
        self.pad = pad or 5

    def build_object(self):
        return tk.Button(
            self.parent._object, text=self.text, command=self.command
        )

    def render_object(self):
        self._object.pack(side=self.side, padx=self.pad, pady=self.pad)


class Form(Frame):
    def __init__(self, data: dict, parent: str=None):
        super().__init__(parent=parent)
        self.entries = data

    def build_data(self, data, parent=None):
        if not parent:
            parent = self
        agg = []
        if isinstance(data, dict):
            for field, value in data.items():
                row = Frame(parent=parent)
                label = Label(text=field, parent=row)
                entry = self.build_data(data=value, parent=row)
                agg.append(row)
            return agg
        elif isinstance(data, list):
            row = Frame(parent=self)
            for field in data:
                entry = self.build_data(field, parent=row)
            agg.append(row)
            return agg
        else:
            entry = Entry(value=data, parent=parent)
            return entry

    def build_children(self):
        agg = self.build_data(self.entries)
        self.nodes = agg
        super().build_children()

    def fetch(self, ent):
        data = {}
        for entry in self.entries:
            field = entry[0]
            text = entry[1].text
            data[field] = text
        return data


class Listbox(Node):
    def __init__(self, values: list=None, parent=None):
        super().__init__(parent=parent)
        self.values = values or []

    def build_object(self):
        node = tk.Listbox(self.parent._object)
        for value in self.values:
            node.insert(tk.END, value)
        return node

    def render_object(self):
        self._object.pack()

    def clear(self):
        self._object.delete(0, tk.END)

    def add(self, value):
        self._object.insert(tk.END, value)


class Scrollbar(Node):
    def render_object(self):
        scrollbar = tk.Scrollbar(self.parent._object)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


class ControlBar(Node):
    def __init__(self, buttons, parent=None):
        super().__init__(parent=parent)
        self.buttons = buttons

    def render_object(self):
        pass


class Panes(Node):
    def __init__(self, panes, parent=None):
        super().__init__(parent=parent)
        self.panes = panes

    def build_object(self):
        return tk.PanedWindow(self.parent._object)

    def render_object(self):
        self._object.pack(fill=tk.BOTH, expand=1)
        for pane in self.panes:
            self._object.add(pane)


class Menu(Node):
    def __init__(self, commands, parent=None):
        super().__init__(parent=parent)
        if not commands:
            commands = []
        self.commands = commands

    def build_object(self):
        menu = tk.Menu(self.parent._object)
        for command in self.commands:
            menu.add_command(label='Wat', command=None)

    def render_object(self):
        pass


class View(Node):
    pass


# a base tab class
class Tab(Node):
    def __init__(self, name: str, parent=None):
        self.name = name
        super().__init__(parent=parent)

    def build_object(self):
        args = []
        if self.parent:
            args.append(self.parent._object)
        return tk.Frame(*args)

    def render_object(self):
        self._object.pack(side=tk.BOTTOM)


# the bulk of the logic is in the actual tab bar
class TabBar(Node):
    def __init__(self, name: str=None, tabs: list=None, parent=None):
        self.tabs = {}
        self.buttons = {}
        self.current_tab = None
        self.name = name
        super().__init__(parent=parent)

    def build_object(self):
        tab_bar = tk.Frame(self.parent._object)
        if self.tabs:
            for tab in tabs:
                pass    #self.add(tab)
        return tab_bar

    def render_object(self):
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
