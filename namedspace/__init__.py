
import sys as _sys

from collections import Container
from collections import Mapping
from collections import Hashable
from collections import MutableMapping

from frozendict import frozendict


def namedspace(typename, required_field_names=(), **kwargs):
    """Builds a new namedspace class.


    """

    # Initialize the list of arguments that will get put into the
    # doc string of the generated class
    arg_list_items = []

    # Inject required_field_names into kwargs so they can be processed
    # just like the other more anonymous keyword arguments.
    kwargs["required_field_names"] = required_field_names

    #
    # Validate parameters
    #
    for arg_name in ("required_field_names", "optional_field_names", "mutable_field_names"):
        arg_value = kwargs.setdefault(arg_name, ())

        if isinstance(arg_value, basestring):
            arg_value = (arg_value,)
            kwargs[arg_name] = arg_value
        elif not isinstance(arg_value, Container):
            raise ValueError("Value for argument '{arg_name}' must be a string or container of strings.".format(
                    arg_name=arg_name))

        for field_name in arg_value:
            if not isinstance(field_name, basestring):
                raise ValueError("Items of container argument '{arg_name}' must be strings.".format(arg_name=arg_name))

        if len(arg_value) != len(frozenset(arg_value)):
            raise ValueError("Value for argument '{arg_name}' contains duplicate field names.".format(
                    arg_name=arg_name))

        arg_list_items.append("{arg_name}={arg_value!r}".format(arg_name=arg_name, arg_value=tuple(arg_value)))

    required_field_names = frozenset(kwargs["required_field_names"])
    optional_field_names = frozenset(kwargs["optional_field_names"])
    all_field_names = required_field_names.union(optional_field_names)

    mutable_field_names = kwargs["mutable_field_names"]
    for field_name in mutable_field_names:
        if field_name not in all_field_names:
            raise ValueError("Mutable field name '{field_name}' is not a required or optional field name.".format(
                    field_name=field_name))

    for arg_name in ("default_values", "default_value_factories"):
        arg_value = kwargs.setdefault(arg_name, {})
        if not isinstance(arg_value, Mapping):
            raise ValueError("Value for argument '{arg_name}' must be a mapping.".format(arg_name=arg_name))

        default_field_names = frozenset(arg_value.iterkeys())
        if not default_field_names.issubset(all_field_names):
            bad_default_field_names = default_field_names - all_field_names
            raise ValueError("Value for argument '{arg_name}' contains invalid field name(s) '{field_names}'.".format(
                    arg_name=arg_name, field_names=", ".join(bad_default_field_names)))

        arg_list_items.append("{arg_name}={arg_value!r}".format(arg_name=arg_name, arg_value=dict(arg_value)))

    default_values = frozendict(kwargs["default_values"])

    default_value_factories = frozendict(kwargs["default_value_factories"])
    for field_name, factory in default_value_factories.iteritems():
        if not callable(factory):
            raise ValueError("Default value factory for '{field_name}' is not callable.".format(field_name=field_name))

    # Fill-in the class template
    class_definition = _class_template.format(
        typename=typename,
        arg_list=", ".join(arg_list_items),
        )

    # Execute the template string in a temporary namespace and support
    # tracing utilities by setting a value for frame.f_globals['__name__']
    namespace = dict(
        __name__='namedspace_{typename}'.format(typename=typename),
        all_field_names=all_field_names,
        required_field_names=required_field_names,
        mutable_field_names=mutable_field_names,
        default_values=default_values,
        default_value_factories=default_value_factories,
        Hashable=Hashable,
        MutableMapping=MutableMapping,
        )

    #
    # Code from here down copied verbatim from namedtuple
    #
    try:
        exec class_definition in namespace
    except SyntaxError as e:
        raise SyntaxError(e.message + ':\n' + class_definition)
    result = namespace[typename]

    # For pickling to work, the __module__ variable needs to be set to the frame
    # where the named tuple is created.  Bypass this step in enviroments where
    # sys._getframe is not defined (Jython for example) or sys._getframe is not
    # defined for arguments greater than 0 (IronPython).
    try:
        result.__module__ = _sys._getframe(1).f_globals.get('__name__', '__main__')
    except (AttributeError, ValueError):
        pass

    return result

_class_template = """\
class {typename}(object):
    "{typename}({arg_list})"

    class FieldNameError(AttributeError, KeyError): pass
    class ReadOnlyNamedspaceError(TypeError): pass
    class ReadOnlyFieldError(TypeError): pass
    class MutableNamedspaceError(TypeError): pass

    _all_field_names = all_field_names
    _required_field_names = required_field_names
    _mutable_field_names = mutable_field_names
    _default_values = default_values
    _default_value_factories = default_value_factories

    def __init__(self, **kwargs):
        self._field_value_storage = dict()

        for field_name, field_value in kwargs.iteritems():
            if field_name in self._all_field_names:
                self._field_value_storage[field_name] = field_value
            else:
                raise ValueError("Field name '{{field_name}} does not exist in the {typename} namedspace.".format(
                        field_name=field_name))

        for field_name in self._all_field_names:
            try:
                field_value = self._get_value(field_name)
            except self.FieldNameError:
                field_value = None

            if field_value in (None, "") and field_name in self._required_field_names:
                raise ValueError("A value for field '{{field_name}}' is required.".format(field_name=field_name))
            elif not field_name in self._field_value_storage:
                self._field_value_storage[field_name] = field_value

    def __repr__(self):
        'Return a nicely formatted representation string'
        return '{typename}({{items!r}})'.format(items=self.as_dict())

    #
    # Generic value access methods
    #
    def _get_value(self, field_name):
        if not field_name in self._all_field_names:
            raise self.FieldNameError("Field name '{{field_name}}' does not exist in the {typename} namedspace.".format(
                    field_name=field_name))

        field_value = self._field_value_storage.get(field_name)
        if field_value is None:
            field_value = self._default_values.get(field_name)
            if field_value is None:
                factory = self._default_value_factories.get(field_name)
                if factory is None:
                    raise self.FieldNameError("Field name '{{field_name}}' does not exist in this {typename}"
                            " namedspace instance.".format(field_name=field_name))
                else:
                    field_value = factory(self)

        return field_value

    def _validate_field_mutability(self, field_name):
        if not field_name in self._all_field_names:
            raise self.FieldNameError("Field '{{field_name}}' does not exist in {typename} namedspace.".format(
                    field_name=field_name))
        if not field_name in self._mutable_field_names:
            if self._mutable_field_names:
                raise self.ReadOnlyFieldError("Field '{{field_name}}' of {typename} namedspace is read-only.".format(
                        field_name=field_name))
            else:
                raise self.ReadOnlyNamedspaceError("{typename} namedspace is read-only.")

    def _set_value(self, field_name, field_value):
        self._validate_field_mutability(field_name)
        self._field_value_storage[field_name] = field_value

    def _del_value(self, field_name):
        self._validate_field_mutability(field_name)
        del self._field_value_storage[field_name]

    #
    # Namedspace API
    #
    @property
    def _field_names(self):
        return self._all_field_names

    @property
    def _field_names_iter(self):
        return iter(self._all_field_names)

    @property
    def _field_values_iter(self):
        for field_name in self._all_field_names:
            yield getattr(self, field_name, None)

    @property
    def _field_values(self):
        return tuple(self._field_values_iter)

    @property
    def _field_items_iter(self):
        for field_name in self._all_field_names:
            yield (field_name, getattr(self, field_name, None))

    @property
    def _field_items(self):
        return frozenset(self._field_items_iter)

    @property
    def _as_dict(self):
        'Return a the namedspace values as a new dictionary.'
        return dict(self._field_items_iter)

    #
    # Attribute API
    #
    def __getattr__(self, attr_name):
        try:
            return self._get_value(attr_name)
        except self.FieldNameError as e:
            raise AttributeError(str(e))

    def __setattr__(self, attr_name, attr_value):
        if attr_name == "_field_value_storage":
            return super({typename}, self).__setattr__(attr_name, attr_value)
        else:
            return self._set_value(attr_name, attr_value)

    def __delattr__(self, attr_name):
        return self._del_value(attr_name)

    #
    # Hashable API
    #
    def __hash__(self):
        if self._mutable_field_names:
            raise self.MutableNamedspaceError("Mutable {typename} namedspace instance is not hashable.")
        else:
            return hash(self._field_values)

    #
    # MutableMapping API
    #
    def __contains__(self, name):
        return name in self._field_names

    def __iter__(self):
        return self._field_names_iter

    def __len__(self):
        return len(self._field_values_iter)

    def __getitem__(self, item_name):
        try:
            return self._get_value(item_name)
        except self.FieldNameError as e:
            raise KeyError(str(e))

    def __setitem__(self, item_name, item_value):
        return self._set_value(item_name, item_value)

    def __delitem__(self, item_name):
        return self._del_value(item_name)


Hashable.register({typename})
MutableMapping.register({typename})
"""
