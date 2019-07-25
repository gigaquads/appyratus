import re

from collections import OrderedDict
from copy import copy, deepcopy
from typing import Dict, Tuple, List, Text, Set


class DictObject(object):
    @classmethod
    def from_list(cls, key, data):
        newdata = OrderedDict()
        for d in data:
            k = getattr(d, key)
            newdata[k] = d
        return cls(newdata)

    def __init__(self, data: Dict = None):
        self.__dict__['data'] = data if data is not None else {}

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __getattr__(self, key):
        return self.data.get(key)

    def __setattr__(self, key, value):
        self.data[key] = value

    def __repr__(self):
        return f'<DictObject({self.data})>'

    def __iter__(self):
        return iter(self.data.items())

    def __contains__(self, key):
        return key in self.data

    def __len__(self):
        return len(self.data)

    def to_dict(self) -> Dict:
        return self.data.copy()


class DictUtils(object):
    """
    # Dict Utils
    """

    @staticmethod
    def key_parts(key) -> Tuple:
        """
        Extract relevant key parts from a key.
        """
        xparts = re.split('^([\w-]+)(\[(\d+)?\])?$', key)
        if len(xparts) == 5:
            # xtype exists, an array referenced has been found in the key.
            _, xkey, xtype, xid, _ = xparts
            xid = int(xid) if xid else xid
        else:
            # normal key
            xkey = key
            xtype, xid = None, None
        return (xkey, xtype, xid)

    @staticmethod
    def flatten_keys(
        data: Dict,
        acc: Dict = None,
        parent: List = None,
        separator: Text = None,
    ) -> Dict:
        """
        Flatten a dictionary, consolidating all nested structures of a value
        into a single key per unique field
        separated by `separator`

        # Args
        - `data`, the data to be flattened
        - `acc`, the accumulator of flattened keys
        - `parent`, the parent key, a list of keys to be joined by the separator
        - `separator`, the separating value when parent key is joined.  by
          default it is the period (`.`)
        """
        if data is None:
            return
        if not data:
            return {}
        data = deepcopy(data)
        if separator is None:
            separator = '.'
        if acc is None:
            acc = {}
        if parent is None:
            parent = []
        if isinstance(data, dict):
            for k, v in data.items():
                kparent = copy(parent)
                kparent.append(str(k))
                vacc = DictUtils.flatten_keys(
                    data=deepcopy(v), acc=acc, separator=separator, parent=kparent
                )
                if isinstance(vacc, dict) and vacc:
                    acc.update(vacc)
                else:
                    acc[separator.join(kparent)] = vacc

        elif isinstance(data, list):
            for idx, v in enumerate(data):
                kparent = copy(parent)
                if kparent:
                    kparent[-1] = '{}[{}]'.format(kparent[-1], str(idx))
                kacc = DictUtils.flatten_keys(
                    data=v, acc=acc, separator=separator, parent=kparent
                )
                if isinstance(kacc, dict):
                    acc.update(kacc)
                else:
                    acc[separator.join(kparent)] = kacc

        else:
            return data
        # da return
        return acc

    @staticmethod
    def unflatten_keys(data: Dict, separator: Text = None) -> Dict:
        """
        # Unflatten keys
        Convert dot-notated keys into nested dictionaries
        """
        if not separator:
            separator = '.'
        new_data = deepcopy(data)

        for k in data.keys():
            if separator in k:
                v = new_data.pop(k)
                path = k.split(separator)
                obj = new_data
                for x in path[:-1]:
                    xkey, xtype, xid = DictUtils.key_parts(x)
                    xval = obj.get(xkey)
                    if not xtype:
                        if not isinstance(xval, dict):
                            if xval:
                                raise ValueError(
                                    'Expected value to be a dictionary, got "{}"'.
                                    format(xval)
                                )
                            obj[xkey] = {}
                    else:
                        if not isinstance(xval, list):
                            if xval:
                                raise ValueError(
                                    'Expected value to be a list, got "{}"'.format(xval)
                                )
                            obj[xkey] = []
                        try:
                            obj[xkey][xid]
                        except IndexError:
                            obj[xkey].insert(xid, {})
                    obj = obj[xkey]
                    if xtype:
                        obj = obj[xid]
                obj[path[-1]] = v
        return new_data

    @staticmethod
    def merge(data: Dict, other: Dict) -> Dict:
        """
        # Merge
        Merge contents of other dictionary into data dictionary.
        """
        new_data = deepcopy(data)
        if not other:
            return new_data
        for other_k, other_v in other.items():
            data_v = new_data.get(other_k, None)
            if isinstance(data_v, dict):
                data_v = DictUtils.merge(data=data_v, other=other_v)
            else:
                data_v = other_v
            new_data[other_k] = data_v
        return new_data

    @staticmethod
    def diff(data: Dict, other: Dict) -> Dict:
        """
        # Diff
        Perform a difference on two dictionaries, returning a dictionary of the
        changed items.

        # Args
        - `data`, the original data structure to be compared against
        - `other`, the modified data to be compared against `data
        """
        changed = None
        if isinstance(data, dict):
            changed = {}
            for k, v in data.items():
                if other:
                    other_v = other.get(k)
                else:
                    other_v = None
                vres = DictUtils.diff(v, other_v)
                if isinstance(vres, (list, dict)):
                    if vres:
                        changed[k] = vres
                elif other and k not in other:
                    changed[k] = v
                elif v is not other_v:
                    changed[k] = other_v
        elif isinstance(data, list):
            changed = []
            for idx, v in enumerate(data):
                if other:
                    if len(other) > idx:
                        other_v = other[idx]
                    else:
                        other_v = None
                else:

                    other_v = None
                vres = DictUtils.diff(v, other_v)
                if vres:
                    changed.append(vres)
        else:
            if data is not other:
                changed = data
        return changed

    @staticmethod
    def remove_keys(
        data: Dict,
        keys: Set = None,
        values: Set = None,
        in_place=False,
    ) -> Dict:
        """
        Providing a list of keys remove them from a dictionary.

        This additionally supports removing keys based on a list of
        values that the key contains.
        """
        if not keys and not values:
            return data if in_place else deepcopy(data)

        if not keys:
            keys = set()
        elif not isinstance(keys, set):
            keys = set(keys)

        if not values:
            values = set()
        elif not isinstance(values, set):
            values = set(values)

        if not isinstance(data, dict):
            raise ValueError(str(data))

        if not in_place:
            new_data = deepcopy(data)
        else:
            new_data = data

        for k, v in data.items():
            if isinstance(v, list):
                vlist = []
                for listk in v:
                    vres = DictUtils.remove_keys(listk, keys, values)
                    if vres in values:
                        del new_data[k]
                    else:
                        vlist.append(vres)
                new_data[k] = vlist
            elif isinstance(v, dict):
                dres = DictUtils.remove_keys(new_data[k], keys, values)
                new_data[k] = dres
            else:
                if k in keys:
                    del new_data[k]
                elif v in values:
                    del new_data[k]
                if k not in new_data:
                    continue
        return new_data

    def traverse(data: Dict, method, depth: int = None) -> Dict:
        """
        Traverse a dictionary while passing values into the provided callable
        in order to mutate existing data
        """
        if not depth:
            depth = 0
        new_data = deepcopy(data)
        if not data:
            return data
        next_depth = depth + 1
        if isinstance(data, dict):
            for kd, vd in data.items():
                if isinstance(vd, (list, dict)):
                    dres = method(kd, vd, depth=depth)
                    dres = DictUtils.traverse(dres, method, depth=next_depth)
                else:
                    dres = method(kd, vd, depth=depth)
                new_data[kd] = dres
        elif isinstance(data, list):
            for kl, vl in enumerate(data):
                if isinstance(vl, (list, dict)):
                    lres = method(kl, vl, depth=depth)
                    lres = DictUtils.traverse(lres, method, depth=next_depth)
                else:
                    lres = method(kl, vl, depth=depth)
                new_data[kl] = lres
        return new_data
