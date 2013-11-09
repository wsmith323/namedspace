
from unittest import TestCase

from mock import Mock

from namedspace import namedspace

class NamedspaceTests(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_default_value = "Mock default value"
        cls.mock_default_factory = Mock(return_value=cls.mock_default_value)
        cls.mock_id = "mock_id"

        cls.TestNamedspace1 = namedspace("TestNamedspace1", "id", optional_field_names=("name", "description", "extra"),
                mutable_field_names=("name", "description"), default_values={"extra": cls.mock_default_value},
                default_value_factories={"name": cls.mock_default_factory})
        cls.test_ns1 = cls.TestNamedspace1(id=cls.mock_id)

        cls.TestNamedspace2 = namedspace("TestNamedspace2", "id", optional_field_names="name",
                                     default_value_factories={"name": cls.mock_default_factory})
        cls.test_ns2 = cls.TestNamedspace2(id=cls.mock_id)

    def test_missing_required_fields(self):
        self.assertRaises(ValueError, self.TestNamedspace1)

    def test_required_fields(self):
        self.assertIs(self.test_ns1.id, self.mock_id)

    def test_mutable_field(self):
        self.assertRaises(self.TestNamedspace1.FieldNameError, lambda: self.test_ns1.description)

        new_value = "new_value"
        self.test_ns1.description = new_value
        self.assertIs(self.test_ns1.description, new_value)

        del self.test_ns1.description

        self.assertRaises(self.TestNamedspace1.FieldNameError, lambda: self.test_ns1.description)

    def test_immutable_field(self):
        self.assertRaises(self.TestNamedspace1.ReadOnlyFieldError,
                lambda: setattr(self.test_ns1, "extra", "new value"))

    def test_immutable_namedspace(self):
        self.assertRaises(self.TestNamedspace2.ReadOnlyNamedspaceError,
                lambda: setattr(self.test_ns2, "name", "new name"))

    def test_default_values(self):
        self.assertIs(self.test_ns1.extra, self.mock_default_value)

    def test_default_value_factories(self):
        self.mock_default_factory.reset_mock()
        self.assertIs(self.test_ns1.name, self.mock_default_value)
        self.mock_default_factory.assert_called_once_with(self.test_ns1)

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
        self.assertEqual(self.test_ns1.name, SubNamedspace._name_tmpl.format(id=self.mock_id))

    def test_overridden_values(self):
        self.assertIn(SubNamedspace._name_tmpl.format(id=self.mock_id), self.test_ns1.values())
