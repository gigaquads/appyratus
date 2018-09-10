from copy import deepcopy
import re


class DictUtils(object):
    @staticmethod
    def unflatten_keys(data: dict, separator=None):
        """
        # Unflatten keys
        Convert dot-notated keys into nested dictionaries
        """
        if not separator:
            separator = '.'
        new_data = deepcopy(data)
        print()
        print('=========== STARTING ===========')
        print('FOUND DATA {} as {}'.format(data, type(data)))
        for k in data.keys():
            print('  PROCESSING KEYS {}'.format(k))
            if separator in k:
                v = new_data.pop(k)
                path = k.split(separator)
                obj = new_data
                print('  OBJECT {} as {}'.format(obj, type(obj)))
                for x in path[:-1]:
                    print('    RESOLVING PATH KEY {}'.format(x))
                    # xtype exists, which means that array has been referenced in the key.
                    xparts = re.split('^([\w-]+)(\[(\d+)?\])?$', x)
                    # its an array in the path
                    if len(xparts) == 5:
                        _, xkey, xtype, xid, _ = xparts
                        xval = obj.get(xkey)
                        print('    ARRAY {} {} {} '.format(xkey, xid, xval))
                        #x = xkey
                        import ipdb; ipdb.set_trace(); print('wat')
                    # it's a normal dictionary
                    else:
                        xkey, xtype, xid = None, None, None
                        xval = obj.get(xkey)
                        print('    FOUND OBJ {} {}'.format(x, xval))
                        xtype = None
                        if xval and not isinstance(xval, dict):
                            raise ValueError(
                                'Expected value to be a dictionary, got "{}"'.
                                format(xval)
                            )
                        elif not isinstance(xval, dict):
                            obj[x] = {}
                        obj = obj[x]
                        print('    {} RES {}'.format(x, obj))
                print('  PATH RESULT {} IN {}'.format(v, path[-1]))
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
