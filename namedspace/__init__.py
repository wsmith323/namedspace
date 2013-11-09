"""
The namedspace factory generates a simple class that encapsulates
a namespace and provides various means to access it.

It is inspired by namedtuple (and shamelessly copies some of the
namedtuple code), and was motivated by my realization that I was
often abusing namedtuple, using it as a base class for simple
custom classes.

In these cases, it was the named attribute access and immutability of
the namedtuple that was desirable, and the sequence behavior was not
needed. In fact, when properties were used to override the returned
value of a named attribute, the values available from the underlying
tuple would not match. Fixing this behavior in a sub-class proved much
more difficult than expected, especially since this is behavior that
wasn't really needed anyway.

So, namedspace was born. Orginally, I called it "namespace" (without
the 'd'), but there was already a namespace project on PyPi, and
calling it "namedspace" gives a nod to its namedtuple ancestry.

Enjoy!

--Warren A. Smith
"""
import sys as _sys

from collections import Container
from collections import Mapping
from collections import Hashable
from collections import MutableMapping

from frozendict import frozendict

_class_template = """\
class {typename}(object):
    "{typename}({arg_list})"

    class FieldNameError(AttributeError, KeyError): pass
    class ReadOnlyNamedspaceError(TypeError): pass
    class ReadOnlyFieldError(TypeError): pass
    class MutableNamedspaceError(TypeError): pass

    _field_names = field_names
    _required_field_names = required_field_names
    _mutable_field_names = mutable_field_names
    _default_values = default_values
    _default_value_factories = default_value_factories

    def __init__(self, **kwargs):
        self._field_values = dict()
        for field_name, field_value in kwargs.iteritems():
            if field_name in self._field_names:
                self._field_values[field_name] = field_value
            else:
                raise ValueError("Field name '{{field_name}} does not exist in the {typename} namedspace.".format(
                        field_name=field_name))
        for field_name in self._required_field_names:
            field_value = self._field_values.get(field_name)
            if field_value is None:
                raise ValueError("A value for field '{{field_name}}' is required.".format(field_name=field_name))

    def __repr__(self):
        'Return a nicely formatted representation string'
        return '{typename}({{items!r}})'.format(items=self.as_dict())

    #
    # Generic value access methods
    #
    def _get_value(self, field_name):
        if not field_name in self._field_names:
            raise self.FieldNameError("Field name '{{field_name}}' does not exist in the {typename} namedspace.".format(
                    field_name=field_name))

        field_value = self._field_values.get(field_name)
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
        if not field_name in self._mutable_field_names:
            if self._mutable_field_names:
                raise self.ReadOnlyFieldError("Field '{{field_name}} of {typename} namedspace is read-only.".format(
                        field_name=field_name))
            else:
                raise self.ReadOnlyNamedspaceError("{typename} namedspace is read-only.")

    def _set_value(self, field_name, field_value):
        self._validate_field_mutability(field_name)
        self._field_values[field_name] = field_value

    def _del_value(self, field_name):
        self._validate_field_mutability(field_name)
        del self._field_values[field_name]

    #
    # Namedspace API
    #
    def field_names(self):
        return self._field_names

    def as_dict(self):
        'Return a the namedspace values as a new dictionary.'
        return dict(self.iteritems())

    #
    # Attribute API
    #
    def __getattr__(self, attr_name):
        return self._get_value(attr_name)

    def __setattr__(self, attr_name, attr_value):
        if attr_name == "_field_values":
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
            return hash(self.values())

    #
    # MutableMapping API
    #
    def __contains__(self, name):
        return name in self.field_names()

    def __iter__(self):
        return iter(self.field_names())

    def __len__(self):
        return len(self.itervalues())

    def __getitem__(self, item_name):
        return self._get_value(item_name)

    def __setitem__(self, item_name, item_value):
        return self._set_value(item_name, item_value)

    def __delitem__(self, item_name):
        return self._del_value(item_name)

    #
    # Dictionary API
    #
    def iteritems(self):
        for field_name in self.field_names():
            yield (field_name, getattr(self, field_name))

    def iterkeys(self):
        return self.iternames()

    def itervalues(self):
        for field_name in self.field_names():
            yield getattr(self, field_name)

    def items(self):
        return frozenset(self.iteritems())

    def keys(self):
        return self.names()

    def values(self):
        return frozenset(self.itervalues())

Hashable.register({typename})
MutableMapping.register({typename})
"""


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
    field_names = required_field_names.union(optional_field_names)

    mutable_field_names = kwargs["mutable_field_names"]
    for field_name in mutable_field_names:
        if field_name not in field_names:
            raise ValueError("Mutable field name '{field_name}' is not a required or optional field name.".format(
                    field_name=field_name))

    for arg_name in ("default_values", "default_value_factories"):
        arg_value = kwargs.setdefault(arg_name, {})
        if not isinstance(arg_value, Mapping):
            raise ValueError("Value for argument '{arg_name}' must be a mapping.".format(arg_name=arg_name))

        default_field_names = frozenset(arg_value.iterkeys())
        if not default_field_names.issubset(field_names):
            bad_default_field_names = default_field_names - field_names
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
        field_names=field_names,
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
