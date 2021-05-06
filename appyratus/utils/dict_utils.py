import re
from collections import (
    OrderedDict,
    defaultdict,
)
from copy import (
    copy,
    deepcopy,
)
from typing import (
    Callable,
    Dict,
    List,
    Set,
    Text,
    Tuple,
)

from .path_utils import PathUtils


class DictObject(object):

    @classmethod
    def from_list(cls, key, data):
        newdata = OrderedDict()
        for d in data:
            k = getattr(d, key)
            newdata[k] = d
        return cls(newdata)

    def __init__(self, data: Dict = None, **more_data):
        if data is not None:
            if more_data:
                data.update(more_data)
        else:
            data = OrderedDict()

        self.__dict__['_data'] = data

    def copy(self) -> 'DictObject':
        return type(self)(self._data)

    def setdefault(self, key, value):
        return self._data.setdefault(key, value)

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __getattr__(self, key):
        if key.startswith('__'):
            # dict object keys can not look like magic methods.
            raise AttributeError(key)
        return self._data.get(key)

    def __setattr__(self, key, value):
        self._data[key] = value

    def __repr__(self):
        return repr(self._data)

    def __iter__(self):
        return iter(self._data.items())

    def __contains__(self, key):
        return key in self._data

    def __len__(self):
        return len(self._data)

    def clear(self):
        self._data.clear()

    def update(self, mapping):
        self._data.update(mapping)

    def pop(self, key, default=None):
        return self._data.pop(key, default)

    def get(self, key, default=None):
        return self._data.get(key, default)

    def values(self):
        return self._data.values()

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def to_dict(self) -> Dict:
        return self._data.copy()


class DictUtils(object):
    """
    # Dict Utils
    """
    #RE_KEY_PARTS = re.compile('^([\w-]+)(\[(\d+|\*)?\])?$')
    RE_KEY_PARTS = re.compile('^([\w-]+)(\[(\d+|\*)?\])?$')

    @classmethod
    def project(cls, data: Dict, keys: List) -> Dict:
        """
        # Project
        Create an projection of an object using the provided keys
        """
        ndata = {}
        # go through all the keys and resolve their values
        for k in keys:
            # split up the key path and get all the parts
            path = PathUtils.get_parts(k, separator='.')
            # set the object of focus to the main data structure and the one we
            # are populating, they should both be at the same level
            dobj = data
            nobj = ndata
            # now iterate over the path parts to get the current key's value
            for idx, path_part in enumerate(path):
                xkey, xref, xid = kparts = cls.key_parts(path_part)

                # determine what kind of value is expected
                val_is_list = xid is not None
                val_is_dict = xid is None
                # we keep track of the last node in order to set the final
                # value in the new data object
                is_last = len(path) - 1 == idx

                # get the associated value from the passed in data
                if dobj is None:
                    dobj = {}
                dval = dobj.get(xkey)
                nval = nobj.get(xkey)

                # key does not exist in data.. skip it
                if xkey not in dobj:
                    continue

                # value is a list
                if val_is_list:
                    # make a new list if it doesn't already exist
                    if not isinstance(nval, list):
                        nobj[xkey] = []

                    # set the final value if terminal, or update the object ref
                    if is_last:
                        nobj[xkey] = [dval[xid]]
                    else:
                        dobj = dval[xid]
                        nobj[xkey].append(dobj)
                        nobj = dobj

                # value is a dict
                elif val_is_dict:
                    if dval is None:
                        dobj[xkey] = {}
                    # set the final value if terminal, or update the object ref
                    if is_last:
                        nobj[xkey] = dval
                        break
                    else:
                        dobj = dobj[xkey]
                        nobj = nobj[xkey]
        return ndata

    @classmethod
    def key_parts(cls, key) -> Tuple:
        """
        Extract relevant key parts from a key.
        """
        xparts = cls.RE_KEY_PARTS.split(key)
        if len(xparts) == 5:
            # xref exists, an array reference has been found in the key.
            _, xkey, xref, xid, _ = xparts
            if xid:
                try:
                    xid = int(xid)
                except:
                    pass
        else:
            # normal key
            xkey = key
            xref, xid = None, None

        return (xkey, xref, xid)

    @classmethod
    def flatten_keys(
        cls,
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
                vacc = cls.flatten_keys(
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
                kacc = cls.flatten_keys(
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

    @classmethod
    def unflatten_keys(cls, data: Dict, separator: Text = None) -> Dict:
        """
        # Unflatten keys
        Convert dot-notated keys into nested dictionaries
        """
        if not separator:
            separator = '.'
        next_data = {}
        # data is a dictionary
        for k, v in data.items():
            obj = next_data
            # here we support more complex keys such as `a.b."c.d"` where
            # `c.d` is a key and not a separator indicating that `d` is a
            # key of dict `c`
            path = PathUtils.get_parts(k, separator='.')

            # now run through the path items and build up the new data
            # structure
            for idx, x in enumerate(path):
                # break apart the key into key parts to determine what the
                # nested structure should look like
                xkey, xref, xid = cls.key_parts(x)
                # misc
                val_is_list = xid is not None
                val_is_dict = xid is None
                is_last = len(path) - 1 == idx

                if obj is None:
                    obj = {}
                objval = obj.get(xkey)

                # value is a dictionary
                if val_is_dict:
                    if objval is None:
                        obj[xkey] = {}
                    # update object reference
                    if is_last:
                        obj[xkey] = v
                        break
                    else:
                        obj = obj[xkey]

                # value is a list
                elif val_is_list:
                    objval = obj.get(xkey)
                    # make a new list if it doesn't already exist
                    if not isinstance(objval, list):
                        obj[xkey] = []
                    # check if the reference index exists and if not then insert it
                    try:
                        obj[xkey][xid]
                    except IndexError:
                        obj[xkey].insert(xid, {})
                    # set value
                    if is_last:
                        obj[xkey][xid] = v
                        break
                    else:
                        # update object reference
                        obj = obj[xkey]
                        obj = obj[xid]

        return next_data

    @classmethod
    def merge(cls, data: Dict, other: Dict, in_place=False) -> Dict:
        """
        # Merge
        Merge contents of other dictionary into data dictionary.
        """
        if in_place:
            new_data = data
        else:
            new_data = deepcopy(data)
        if not other:
            return new_data or {}
        for other_k, other_v in other.items():
            data_v = new_data.get(other_k, None)
            if isinstance(data_v, dict):
                data_v = cls.merge(data=data_v, other=other_v)
            else:
                data_v = other_v
            new_data[other_k] = data_v
        return new_data

    @classmethod
    def diff(cls, data: Dict, other: Dict) -> Dict:
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
                    if isinstance(other, str):
                        other_v = v
                    else:
                        other_v = other.get(k)
                else:
                    other_v = None
                vres = cls.diff(v, other_v)
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
                vres = cls.diff(v, other_v)
                if vres:
                    changed.append(vres)
        else:
            if data is not other:
                changed = data
        return changed

    @classmethod
    def remove_keys(
        cls,
        data: Dict,
        keys: Set = None,
        values: Set = None,
        empty_values: Set = None,
        in_place=False,
    ) -> Dict:
        """
        Providing a list of keys remove them from a dictionary.

        This additionally supports removing keys based on a list of
        values that the key contains.
        """

        if not in_place:
            new_data = deepcopy(data)
        else:
            new_data = data

        if not keys and values is None and not empty_values:
            # no operations provided, nothing to do here
            return new_data

        def make_set(data):
            set_data = None
            if data is None:
                set_data = set()
            elif isinstance(data, set):
                set_data = data
            elif isinstance(data, (list, tuple)):
                set_data = set(data)
            else:
                set_data = set([data])
            return set_data

        keys = make_set(keys)
        values = make_set(values)
        empty_values = make_set(empty_values)

        if isinstance(new_data, list):
            vlist = []
            for idx, v in enumerate(new_data):
                vres = cls.remove_keys(v, keys, values, empty_values)
                if vres not in values:
                    vlist.append(vres)
            new_data = vlist
        elif isinstance(new_data, dict):
            vdict = {}
            for k, v in new_data.items():
                vres = cls.remove_keys(v, keys, values, empty_values)
                if k in keys:
                    continue
                if not isinstance(vres, (list, dict)) and vres in values:
                    continue
                if type(vres) in empty_values and not vres:
                    continue
                vdict[k] = vres
            new_data = vdict

        return new_data

    @classmethod
    def traverse(
        cls,
        data: Dict,
        method,
        depth: int = None,
        acc: Dict = None,
        **kwargs,
    ) -> Dict:
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
                    dres = method(kd, vd, depth=depth, **kwargs)
                    dres = cls.traverse(dres, method, depth=next_depth, **kwargs)
                else:
                    dres = method(kd, vd, depth=depth, **kwargs)
                new_data[kd] = dres
        elif isinstance(data, list):
            for kl, vl in enumerate(data):
                if isinstance(vl, (list, dict)):
                    lres = method(kl, vl, depth=depth, **kwargs)
                    lres = cls.traverse(lres, method, depth=next_depth, **kwargs)
                else:
                    lres = method(kl, vl, depth=depth, **kwargs)
                new_data[kl] = lres
        return new_data

    @classmethod
    def index(cls, key, records: List[Dict]) -> Dict:
        index = {}
        for record in records:
            try:
                k = record[key]
            except Exception as error:
                raise error
            if k not in index:
                index[k] = [record]
            else:
                index[k].append(record)
        return index

    @classmethod
    def keep(cls, condition, records) -> List:
        return [x for x in records if condition(x)]

    @classmethod
    def map(cls, mapper: Callable, record: Dict) -> Dict:
        mapped_records = []
        for k, v in records.items():
            k_mapped, v_mapped = mapper(k, v)
            mapped_records[k_mapped] = v_mapped
        return mapped_records
