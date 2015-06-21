
import sys as _sys

from collections import Container
from collections import Hashable
from collections import Mapping
from collections import MutableMapping
from collections import OrderedDict

from frozendict import frozendict


def namedspace(typename, required_fields=(), optional_fields=(), mutable_fields=(),
        default_values=frozendict(), default_value_factories=frozendict(),
        return_none=False):
    """Builds a new class that encapsulates a namespace and provides
    various ways to access it.


    The typename argument is required and is the name of the
    namedspace class that will be generated.

    The required_fields and optional_fields arguments can be a string
    or sequence of strings and together specify the fields that
    instances of the namedspace class have.

    Values for the required fields must be provided somehow when the
    instance is created. Values for optional fields may be provided
    later, or maybe not at all.

    If an optional field is queried before its value has been set,
    an AttributeError will be raised. This behavior can be altered
    to cause None to be returned instead by setting the return_none
    keyword argument to True.

    The mutable_fields argument specifies which fields will be mutable,
    if any. By default, all fields are immutable and all instances are
    hashable and can be used as dictionary keys. If any fields are set
    as mutable, all instances are not hashable and cannot be used as
    dictionary keys.

    The default_values mapping provides simple default values for the
    fields.

    The default_value_factories mapping provides a more flexible, but
    more complex, mechanism for providing default values. The value of
    each item is a callable that takes a single argument, the
    namedspace instance, and returns the default value for the field.

    The default_values_factories mapping is only consulted if there
    is no default value for the field in the default_values mapping.


    Here is a simple example, using only the required fields argument:

    >>> SimpleNS = namedspace("SimpleNS", ("id", "name", "description"))

    >>> SimpleNS
    <class 'namedspace.SimpleNS'>

    There are built-in properties to access collections and iterators
    associated with the namespace class.

    >>> SimpleNS._field_names
    ('id', 'name', 'description')

    >>> tuple(SimpleNS._field_names_iter)
    ('id', 'name', 'description')

    Once the class has been created, it can be instantiated like any
    other class. However, a value for all of the required fields must
    be provided.

    >>> simple_ns = SimpleNS(id=1, description="Simple Description")
    Traceback (most recent call last):
        <snip/>
    ValueError: A value for field 'name' is required.

    >>> simple_ns = SimpleNS(id=1, name="Simple Name", description="Simple Description")

    >>> simple_ns
    SimpleNS(id=1, name='Simple Name', description='Simple Description')


    An instance of a namedspace class provides standard attribute
    access to its fields.

    >>> simple_ns.id
    1
    
    >>> simple_ns.name
    'Simple Name'
    
    >>> simple_ns.description
    'Simple Description'


    In addition to standard attribute access, instances of a namedspace
    class implement a MutableMapping interface.

    >>> 'id' in simple_ns
    True

    >>> for field_name in simple_ns:
    ...     print field_name
    id
    name
    description

    >>> len(simple_ns)
    3

    >>> simple_ns["id"]
    1

    >>> simple_ns["name"]
    'Simple Name'

    >>> simple_ns["description"]
    'Simple Description'


    There are built-in properties to access collections and iterators
    associated with the namespace.

    The namespace encapsulated by a namedspace class is stored in an
    OrderedDict, so order of the collections is the same as the order
    that the fields were specified.

    All of these properties use the standard "non-public" naming
    convention in order to not pollute the public namespace.

    >>> simple_ns._field_names
    ('id', 'name', 'description')

    >>> tuple(simple_ns._field_names_iter)
    ('id', 'name', 'description')

    >>> simple_ns._field_values
    (1, 'Simple Name', 'Simple Description')

    >>> tuple(simple_ns._field_values_iter)
    (1, 'Simple Name', 'Simple Description')

    >>> simple_ns._field_items
    [('id', 1), ('name', 'Simple Name'), ('description', 'Simple Description')]

    >>> list(simple_ns._field_items_iter)
    [('id', 1), ('name', 'Simple Name'), ('description', 'Simple Description')]

    >>> simple_ns._as_dict
    OrderedDict([('id', 1), ('name', 'Simple Name'), ('description', 'Simple Description')])


    Here is a more complex example, using most of the other arguments:

    >>> from itertools import count

    >>> ComplexNS = namedspace("ComplexNS", "id", optional_fields=("name", "description", "extra"),
    ...     mutable_fields=("description", "extra"), default_values={"description": "None available"},
    ...     default_value_factories={"id": lambda self, counter=count(start=1): counter.next(),
    ...         "name": lambda self: "Name for id={id}".format(id=self.id)})

    >>> complex_ns1 = ComplexNS()

    >>> complex_ns1.id
    1

    The value of 1 was automatically assigned by the
    default_value_factory for the 'id' field, in this case a lambda
    closure that hooks up an instance of itertools.count.

    >>> complex_ns1.name
    'Name for id=1'

    This value was also generated by a default value factory. In this
    case, the factory for the 'name' attribute uses the value of the
    'id' attribute to compute the default value.

    >>> complex_ns1.description
    'None available'

    This value came from the default_values mapping.


    The description field was set as a mutable field, which allows
    it to be modified.

    >>> complex_ns1.description = "Some fancy description"
    >>> complex_ns1.description
    'Some fancy description'

    Its value can also be deleted.

    >>> del complex_ns1.description
    >>> complex_ns1.description
    'None available'

    Since its modified value was deleted, and it has a default value,
    it has reverted to its default value.


    The extra field is a valid field in this namedspace, but it has not
    yet been assigned a value and does not have a default.
     
    >>> complex_ns1.extra
    Traceback (most recent call last):
        <snip/>
    AttributeError: "Field 'extra' does not yet exist in this ComplexNS namedspace instance."

    Sometimes, having an exception raised if an optional field is
    missing, and being forced to handle it, is annoying. A namedspace
    class can be configured at creation time to return None instead of
    raising exceptions for optional fields by setting the `return_none`
    parameter to `True`. Here is a trivial example:

    >>> QuietNS = namedspace("QuietNS", optional_fields=("might_be_none",), return_none=True)

    >>> quiet_ns1 = QuietNS(might_be_none="Nope, not this time")
    >>> quiet_ns1.might_be_none
    'Nope, not this time'

    >>> quiet_ns2 = QuietNS()
    >>> quiet_ns2.might_be_none
    >>>

    Having the namedspace quietly return `None` makes sense in some
    situations. But be careful. Understand the full implications of
    this alternate behavior on the code that uses it. Subtle data-
    dependent bugs can be introduced by this behavior, which is why it
    is not enabled by default.

    Now, back to our "complex" example.

    Since the 'extra' field is one of the mutable fields, we can give it a value.

    >>> complex_ns1.extra = "Lasts a long, long time"
    >>> complex_ns1.extra
    'Lasts a long, long time'

    Only fields that have been declared as either required or optional
    are allowed.

    >>> complex_ns1.some_other_field = "some other value"
    Traceback (most recent call last):
        <snip/>
    FieldNameError: "Field 'some_other_field' does not exist in ComplexNS namedspace."

    Finally, to illustrate that our counter is working as it should, if
    we instantiate another instance, our id field will get the next
    counter value.

    >>> complex_ns2 = ComplexNS()
    >>> complex_ns2.id
    2

    A common use case for a namedspace class is as a base class for
    another custom class that has additional members such as properties
    and methods. This way, the custom class gets all of the namedspace
    behavior through declarative configuration, instead of having
    to re-define that behavior imperatively.

    Here is a (fairly contrived) example:

    >>> from collections import Counter, OrderedDict
    >>> _Widget = namedspace("_Widget", ("mfg_code", "model_code", "serial_number"), optional_fields=("sku", "pk"),
    ...         return_none=True)
    >>> class Widget(_Widget):
    ...     _sn_map = Counter()
    ...     def __init__(self, *args, **kwargs):
    ...         sn_key = (kwargs["mfg_code"], kwargs["model_code"])
    ...         self._sn_map[sn_key] += 1
    ...         kwargs["serial_number"] = "{:010}".format(self._sn_map[sn_key])
    ...         super(Widget, self).__init__(*args, **kwargs)
    ...     @property
    ...     def sku(self):
    ...         return "{}_{}".format(self.mfg_code, self.model_code)
    ...     @property
    ...     def pk(self):
    ...         return "{}_{}".format(self.sku, self.serial_number)
    >>> widget1 = Widget(mfg_code="ACME", model_code="X-500")
    >>> widget1
    Widget(mfg_code='ACME', model_code='X-500', serial_number='0000000001', sku='ACME_X-500', pk='ACME_X-500_0000000001')
    >>> widget1._as_dict
    OrderedDict([('mfg_code', 'ACME'), ('model_code', 'X-500'), ('serial_number', '0000000001'), ('sku', 'ACME_X-500'), ('pk', 'ACME_X-500_0000000001')])
    >>> widget2 = Widget(mfg_code="ACME", model_code="X-500")
    >>> widget2
    Widget(mfg_code='ACME', model_code='X-500', serial_number='0000000002', sku='ACME_X-500', pk='ACME_X-500_0000000002')
    >>> widget2._as_dict
    OrderedDict([('mfg_code', 'ACME'), ('model_code', 'X-500'), ('serial_number', '0000000002'), ('sku', 'ACME_X-500'), ('pk', 'ACME_X-500_0000000002')])
    """

    # Initialize the list of arguments that will get put into the
    # doc string of the generated class
    arg_list_items = []

    #
    # Validate parameters
    #
    for arg_name in ("required_fields", "optional_fields", "mutable_fields"):
        arg_value = locals()[arg_name]

        if isinstance(arg_value, basestring):
            arg_value = (arg_value,)
            exec "{arg_name} = arg_value".format(arg_name=arg_name)
        elif not isinstance(arg_value, Container):
            raise ValueError("Value for argument '{arg_name}' must be a string or container of strings.".format(
                    arg_name=arg_name))

        for field_name in arg_value:
            if not isinstance(field_name, basestring):
                raise ValueError("Items of container argument '{arg_name}' must be strings.".format(arg_name=arg_name))

        if len(arg_value) != len(frozenset(arg_value)):
            raise ValueError("Value for argument '{arg_name}' contains duplicate fields.".format(
                    arg_name=arg_name))

        arg_list_items.append("{arg_name}={arg_value!r}".format(arg_name=arg_name, arg_value=tuple(arg_value)))

        exec "{arg_name}_set = frozenset(arg_value)".format(arg_name=arg_name)

    all_fields = tuple(required_fields + optional_fields)

    if not all_fields:
        raise ValueError("At least one required or optional field must be provided.")

    all_fields_set = frozenset(all_fields)

    for field_name in mutable_fields:
        if field_name not in all_fields_set:
            raise ValueError("Mutable field '{field_name}' is not a required or optional field.".format(
                    field_name=field_name))

    for arg_name in ("default_values", "default_value_factories"):
        arg_value = locals()[arg_name]
        if not isinstance(arg_value, Mapping):
            raise ValueError("Value for argument '{arg_name}' must be a mapping.".format(arg_name=arg_name))

        default_field_names = frozenset(arg_value.iterkeys())
        if not default_field_names.issubset(all_fields_set):
            bad_default_field_names = default_field_names - all_fields_set
            raise ValueError("Value for argument '{arg_name}' contains invalid field(s) '{field_names}'.".format(
                    arg_name=arg_name, field_names=", ".join(bad_default_field_names)))

        arg_list_items.append("{arg_name}={arg_value!r}".format(arg_name=arg_name, arg_value=dict(arg_value)))

        exec "{arg_name} = frozendict(arg_value)".format(arg_name=arg_name)

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
        all_fields=all_fields,
        all_fields_set=all_fields_set,
        required_fields_set=locals()["required_fields_set"],
        mutable_fields_set=locals()["mutable_fields_set"],
        default_values=default_values,
        default_value_factories=default_value_factories,
        Hashable=Hashable,
        MutableMapping=MutableMapping,
        OrderedDict=OrderedDict,
        return_none=return_none,
        NamedspaceMeta=NamedspaceMeta,
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


class NamedspaceMeta(type):
    "Metaclass for namedspace classes"

    @property
    def _field_names(self):
        return self._all_fields

    @property
    def _field_names_iter(self):
        return iter(self._all_fields)


_class_template = """\
class {typename}(object):
    __metaclass__ = NamedspaceMeta
    "{typename}({arg_list})"

    class FieldNameError(AttributeError, KeyError): pass
    class ReadOnlyNamedspaceError(TypeError): pass
    class ReadOnlyFieldError(TypeError): pass
    class MutableNamedspaceError(TypeError): pass

    _all_fields = all_fields
    _all_fields_set = all_fields_set
    _required_fields_set = required_fields_set
    _mutable_fields_set = mutable_fields_set
    _default_values = default_values
    _default_value_factories = default_value_factories
    _return_none = return_none

    def __init__(self, **kwargs):
        self._field_value_storage = OrderedDict()

        for field_name, field_value in kwargs.iteritems():
            if field_name in self._all_fields_set:
                self._field_value_storage[field_name] = field_value
            else:
                raise ValueError("field '{{field_name}} does not exist in the {typename} namedspace.".format(
                        field_name=field_name))

        for field_name in self._field_names:
            try:
                field_value = self._get_value(field_name)
            except self.FieldNameError:
                field_value = None

            if field_value in (None, "") and field_name in self._required_fields_set:
                raise ValueError("A value for field '{{field_name}}' is required.".format(field_name=field_name))
            elif not field_name in self._field_value_storage:
                self._field_value_storage[field_name] = field_value

    def __repr__(self):
        'Return a nicely formatted representation string'
        return '{{clsname}}({{items}})'.format(clsname=self.__class__.__name__,
            items=", ".join("{{name}}={{value!r}}".format(name=name, value=value)
                for name, value in self._field_items))

    #
    # Generic value access methods
    #
    def _get_value(self, field_name):
        if not field_name in self._all_fields_set:
            raise self.FieldNameError("Field '{{field_name}}' does not exist in the {typename} namedspace.".format(
                    field_name=field_name))

        field_value = self._field_value_storage.get(field_name)
        if field_value is None:
            field_value = self._default_values.get(field_name)
            if field_value is None:
                factory = self._default_value_factories.get(field_name)
                if factory is None:
                    if self._return_none:
                        return None
                    else:
                        raise self.FieldNameError("Field '{{field_name}}' does not yet exist in this {typename}"
                                " namedspace instance.".format(field_name=field_name))
                else:
                    field_value = factory(self)

        return field_value

    def _validate_field_mutability(self, field_name):
        if not field_name in self._all_fields_set:
            raise self.FieldNameError("Field '{{field_name}}' does not exist in {typename} namedspace.".format(
                    field_name=field_name))
        if not field_name in self._mutable_fields_set:
            if self._mutable_fields_set:
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
        return self.__class__._field_names

    @property
    def _field_names_iter(self):
        return self.__class__._field_names_iter

    @property
    def _field_values_iter(self):
        for field_name in self._field_names:
            yield getattr(self, field_name, None)

    @property
    def _field_values(self):
        return tuple(self._field_values_iter)

    @property
    def _field_items_iter(self):
        for field_name in self._field_names:
            yield (field_name, getattr(self, field_name, None))

    @property
    def _field_items(self):
        return list(self._field_items_iter)

    @property
    def _as_dict(self):
        'Return a the namedspace values as a new ordered dictionary.'
        return OrderedDict(self._field_items_iter)

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
        if self._mutable_fields_set:
            raise self.MutableNamedspaceError("Mutable {typename} namedspace instance is not hashable.")
        else:
            return hash(self._field_values)

    #
    # Needed along with Hashable API to use this instance as dictionary key
    #
    def __eq__(self, obj):
        return isinstance(obj, self.__class__) and obj._field_items == self._field_items

    #
    # MutableMapping API
    #
    def __contains__(self, name):
        return name in self._field_names

    def __iter__(self):
        return self._field_names_iter

    def __len__(self):
        return len(self._field_values)

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
