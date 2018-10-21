from copy import copy, deepcopy
import re


class DictUtils(object):
    @staticmethod
    def key_parts(key) -> tuple:
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
    def flatten(
        data: dict, acc: dict=None, parent: list=None, separator=None
    ) -> dict:
        """
        Flatten a dictionary, consolidating all nested structures of a value
        into a single key per unique field
        separated by `separator`

        Args
        - `data`, the data to be flattened
        - `acc`, the accumulator of flattened keys
        - `parent`, the parent key, a list of keys to be joined by the separator
        - `separator`, the separating value when parent key is joined.  by
          default it is the period (`.`)
        """
        if not data:
            return {}
        if not separator:
            separator = '.'
        if not acc:
            acc = {}
        if not parent:
            parent = []
        if isinstance(data, list):
            for idx, v in enumerate(data):
                kparent = copy(parent)
                kparent[-1] = '{}[{}]'.format(kparent[-1], str(idx))
                kacc = DictUtils.flatten(
                    v, separator=separator, parent=kparent
                )
                acc.update(kacc)
        elif isinstance(data, dict):
            for k, v in data.items():
                kparent = copy(parent)
                kparent.append(k)
                kacc = DictUtils.flatten(
                    v, separator=separator, parent=kparent
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
    def unflatten_keys(data: dict, separator=None):
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
                                    'Expected value to be a list, got "{}"'.
                                    format(xval)
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
    def merge(data: dict, other: dict):
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
    def diff(data: dict, other: dict) -> dict:
        """
        # Diff
        Perform a difference on two dictionaries, returning a dictionary of the
        changed items.
        """
        changed = {}
        for data_k, data_v in data.items():
            if other:
                other_v = other.get(data_k)
            else:
                other_v = None
            if isinstance(data_v, dict):
                data_v = DictUtils.diff(data_v, other_v)
                if data_v:
                    changed[data_k] = data_v
            elif other and data_k not in other:
                changed[data_k] = data_v
            elif data_v is not other_v:
                changed[data_k] = other_v
        return changed

    @staticmethod
    def remove_keys(data: dict, keys: list=None, values: list=None):
        """
        Providing a list of keys remove them from a dictionary.

        This additionally supports removing keys based on a list of values that
        the key contains.
        """
        if not keys and not values:
            return data
        if not keys:
            keys = []
        if not values:
            values = []
        if not isinstance(data, dict):
            return data
        new_data = deepcopy(data)
        for k, v in data.items():
            if k in keys:
                new_data.pop(k)
            elif v in values:
                new_data.pop(k)
            if k not in new_data:
                continue
            if isinstance(v, list):
                vlist = []
                for listk in v:
                    vres = DictUtils.remove_keys(listk, keys, values)
                    if vres in values:
                        new_data.pop(k)
                    else:
                        vlist.append(vres)
                new_data[k] = vlist
            elif isinstance(v, dict):
                dres = DictUtils.remove_keys(new_data[k], keys, values)
                if dres in values:
                    new_data.pop(k)
                else:
                    new_data[k] = dres
        return new_data

    def traverse(data: dict, method):
        new_data = deepcopy(data)
        if not data:
            return data
        if isinstance(data, dict):
            for kd, vd in data.items():
                if isinstance(vd, (list, dict)):
                    dres = DictUtils.traverse(vd, method)
                else:
                    dres = method(vd)
                new_data[kd] = dres
        elif isinstance(data, list):
            for kl, vl in enumerate(data):
                if isinstance(vl, (list, dict)):
                    lres = DictUtils.traverse(vl, method)
                else:
                    lres = method(vl)
                new_data[kl] = lres
        return new_data

    def traverse_orig(data: dict, method):
        if not data:
            return data
        if isinstance(data, dict):
            for kd, vd in data.items():
                if isinstance(vd, (list, dict)):
                    yield from DictUtils.traverse(vd, method)
                else:
                    yield (kd, method(vd))
        elif isinstance(data, list):
            for kl, vl in enumerate(data):
                if isinstance(vl, (list, dict)):
                    yield from DictUtils.traverse(vl, method)
                else:
                    yield (kl, method(vl))
        return data
