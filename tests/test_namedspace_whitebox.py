
from unittest import TestCase

from namedspace import namedspace

class NamedspaceTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_default_value = "Mock default value"
        cls.mock_name_template = "Mock name for {id}"
        cls.mock_default_factory = staticmethod(lambda ns: cls.mock_name_template.format(id=ns.id))
        cls.mock_id = "mock_id"

        cls.TestNamedspace1 = namedspace("TestNamedspace1", "id", optional_fields=("name", "description", "extra"),
                mutable_fields=("name", "description"), default_values={"extra": cls.mock_default_value},
                default_value_factories={"name": cls.mock_default_factory})
        cls.test_ns1 = cls.TestNamedspace1(id=cls.mock_id)

        cls.TestNamedspace2 = namedspace("TestNamedspace2", "id", optional_fields="name",
                default_value_factories={"name": cls.mock_default_factory})
        cls.test_ns2 = cls.TestNamedspace2(id=cls.mock_id)

    def test_missing_required_fields(self):
        """
        A ValueError should be raised when a namedspace class is
        instantiated without values for required fields.
        """
        self.assertRaises(ValueError, self.TestNamedspace1)

    def test_required_fields(self):
        """
        Values passed as values for required fields when a
        namedspace class is instantiated should be available as
        attributes on the instance.
        """
        self.assertIs(self.test_ns1.id, self.mock_id)

    def test_mutable_fields(self):
        """
        Fields designated as mutable should be modifiable.
        """
        self.assertRaises(AttributeError, lambda: self.test_ns1.description)

        new_value = "new_value"
        self.test_ns1.description = new_value
        self.assertIs(self.test_ns1.description, new_value)

        del self.test_ns1.description

        self.assertRaises(AttributeError, lambda: self.test_ns1.description)

    def test_immutable_fields(self):
        """
        Fields not designated as mutable should be read-only.
        """
        self.assertRaises(self.TestNamedspace1.ReadOnlyFieldError,
                lambda: setattr(self.test_ns1, "extra", "new value"))

    def test_immutable_namedspace(self):
        """
        Namedspaces that have no mutable fields should consider themselves read-only.
        """
        self.assertRaises(self.TestNamedspace2.ReadOnlyNamedspaceError,
                lambda: setattr(self.test_ns2, "name", "new name"))

    def test_namedspace_hashable(self):
        """
        Immutable namedspaces should be hashable. Mutable namedspaces should not be.
        """
        self.assertRaises(self.TestNamedspace1.MutableNamedspaceError, lambda: hash(self.test_ns1))

        ns2_hash = hash(self.test_ns2)
        self.assertIsInstance(ns2_hash, int)

    def test_default_values(self):
        """
        Default values for fields should be retrieved (if they exist)
        from the default_values mapping provided when the namedspace
        class was generated.
        """
        self.assertIs(self.test_ns1.extra, self.mock_default_value)

    def test_default_value_factories(self):
        """
        Default values for fields should be retrieved by acquiring
        the default factory for a field (if it exists) from the
        default_value_factories mapping provided when the namedspace
        class was generated, calling the factory and passing the
        namedspace instance to it, and returning the resulting value.
        """
        self.assertEqual(self.test_ns1.name, self.mock_name_template.format(id=self.test_ns1.id))

    def test_field_names(self):
        """
        The _field_names property should return the correct values.
        """
        self.assertEqual(self.test_ns1._field_names, ("id", "name", "description", "extra"))

    def test_field_values(self):
        """
        The _field_values property should return the correct values.
        """
        self.assertEqual(frozenset(self.test_ns1._field_values), frozenset((
                self.test_ns1.id,
                self.test_ns1.name,
                getattr(self.test_ns1, "description", None),
                self.test_ns1.extra,
            )))

    def test_field_items(self):
        """
        The _field_items property should return the correct values.
        """
        self.assertEqual(self.test_ns1._field_items, [
                ("id", self.test_ns1.id),
                ("name", self.test_ns1.name),
                ("description", getattr(self.test_ns1, "description", None)),
                ("extra", self.test_ns1.extra),
            ])


class SubNamedspace(namedspace("_SubNamedspace", ("id", "name"))):
    _name_tmpl = "Overridden name for {id}"

    @property
    def name(self):
        return self._name_tmpl.format(id=self.id)


class SubNamedspaceTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_id = "mock_id"
        cls.mock_name = "mock_name"
        cls.test_ns1 = SubNamedspace(id=cls.mock_id, name=cls.mock_name)

    def test_overridden_property(self):
        """
        Properties with the same name as namedspace fieldnames should
        override the field values.
        """
        self.assertEqual(self.test_ns1.name, SubNamedspace._name_tmpl.format(id=self.mock_id))

    def test_overridden_values(self):
        """
        Overridden property values should properly appear in value collections.
        """
        self.assertIn(SubNamedspace._name_tmpl.format(id=self.mock_id), self.test_ns1._field_values)
