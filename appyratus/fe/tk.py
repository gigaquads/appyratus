import copy
import tkinter as tk

from appyratus.util import DictUtils


class Node(object):
    """
    # Node
    Represents any particular node in a tree of gui elements.  Specific types
    of Nodes implement this, such as `Frame` and `Label`.
    """

    def __repr__(self):
        value = getattr(self, 'value', None)
        value_str = str(value)[0:32] if value else value
        text = getattr(self, 'text', None)

        return "<Node({}#{}){}>".format(
            self.__class__.__name__,
            str(id(self))[-4:],
            ' value={}/"{}"'.format(value.__class__.__name__, value_str)
            if value else ''
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
        print(
            '{} {} ({})'.
            format('  ' * self.depth, repr(self), len(self.nodes))
        )
        self._object = self.build_object()
        self.build_children()

    def build_children(self):
        for node in self.nodes:
            node.build()

    def render(self):
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
    def __init__(self, key=None, value=None, parent=None):
        self.key = key
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
        self.data = data
        self.entries = []

    def build_data(self, key=None, value=None, parent=None):
        """
        Build form data as entries.  This will recurisively iterate over nested
        data structures and provide a generic layout of entry fields

        # Args
        - `key`, the current key.  This is a list of keys, depending on the
          depth of the value being built.  When attached to an entry, it will
          be flattened into a dotted path, `path.to.key`
        - `value`, the provided data structure that is being built
        - `parent`, the parent of the data structure
        """
        if not key:
            key = []
        if not parent:
            parent = self
        if isinstance(value, dict):
            for kfield, kvalue in value.items():
                base_key = copy.copy(key)
                base_key.append(kfield)
                row = Frame(parent=parent)
                label = Label(text=kfield, parent=row)
                self.build_data(key=base_key, value=kvalue, parent=row)
        elif isinstance(value, list):
            row = Frame(parent=parent)
            for idx, field in enumerate(value):
                base_key = copy.copy(key)
                base_key.append(str(idx))
                self.build_data(key=base_key, value=field, parent=parent)
        else:
            entry = Entry(key=key, value=value, parent=parent)
            self.entries.append(entry)

    def build_children(self):
        agg = self.build_data(value=self.data)
        super().build_children()

    def fetch(self, ent):
        flat_data = {}
        for entry in self.entries:
            key = entry.key
            text = entry.text
            flat_data['.'.join(key)] = text
        data = DictUtils.unflatten_keys(data=flat_data)
        import ipdb; ipdb.set_trace(); print('wat')
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
