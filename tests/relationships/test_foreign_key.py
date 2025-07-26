from django import test
from django.db import models
from rest_framework.serializers import ModelSerializer

from drf_nested_model_serilaizer.serializer import NestedModelSerializer
from tests.relationships.test_relationship import RelationshipTest


class ForeignKeyNestedModel(models.Model):
    name = models.CharField()


class ForeignKeyParentModel(models.Model):
    nested = models.ForeignKey(
        ForeignKeyNestedModel, on_delete=models.CASCADE, null=True
    )


class ForeignKeyNestedModelSerializer(ModelSerializer):
    class Meta:
        model = ForeignKeyNestedModel
        fields = ("id", "name")


class ForeignKeyParentSerializer(NestedModelSerializer):
    nested = ForeignKeyNestedModelSerializer(required=False, allow_null=True)

    class Meta:
        model = ForeignKeyParentModel
        fields = ("id", "nested")


class ForeignKeyTest(RelationshipTest, test.TestCase):
    def test_create_omit_no(self):
        data = {}
        expected_valid = True
        expected = {"id": 1, "nested": None}

        serializer = ForeignKeyParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_none_no(self):
        data = {"nested": None}
        expected_valid = True
        expected = {"id": 1, "nested": None}

        serializer = ForeignKeyParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_empty_no(self):
        pass

    def test_create_withoutpk_no(self):
        data = {"nested": {"name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 1, "nested": {"id": 1, "name": "Max Mustermann"}}

        serializer = ForeignKeyParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_withnonepk_no(self):
        data = {"nested": {"id": None, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 1, "nested": {"id": 1, "name": "Max Mustermann"}}

        serializer = ForeignKeyParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_onlypk_no(self):
        data = {"nested": {"id": 3}}
        expected_valid = True
        expected = {"id": 1, "nested": {"id": 3, "name": "Max Mustermann"}}

        ForeignKeyNestedModel.objects.create(id=3, name="Max Mustermann")

        serializer = ForeignKeyParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_withpk_no(self):
        data = {"nested": {"id": 3, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 1, "nested": {"id": 3, "name": "Max Mustermann"}}

        ForeignKeyNestedModel.objects.create(id=3, name="Erika Musterfrau")

        serializer = ForeignKeyParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_multiple_no(self):
        data_list = [
            {},  # Omit
            {"nested": None},  # None
            {"nested": {"name": "Max Mustermann"}},  # Without pk
            {"nested": {"id": None, "name": "Erika Musterfrau"}},  # With `None` pk
            {"nested": {"id": 3}},  # Only pk
            {"nested": {"id": 5, "name": "Paul Beispielmann"}},  # With pk
        ]
        expected_valid = True
        expected_list = [
            {"id": 1, "nested": None},
            {"id": 2, "nested": None},
            {"id": 3, "nested": {"id": 6, "name": "Max Mustermann"}},
            {"id": 4, "nested": {"id": 7, "name": "Erika Musterfrau"}},
            {"id": 5, "nested": {"id": 3, "name": "Erna Beispielfrau"}},
            {"id": 6, "nested": {"id": 5, "name": "Paul Beispielmann"}},
        ]

        ForeignKeyNestedModel.objects.create(id=3, name="Erna Beispielfrau")
        ForeignKeyNestedModel.objects.create(id=5, name="John Doe")

        instance_list = []
        for i in range(len(data_list)):
            data = data_list[i]

            serializer = ForeignKeyParentSerializer(data=data)
            assert serializer.is_valid() == expected_valid, serializer.errors
            instance_list.append(serializer.save())

        for i in range(max(len(data_list), len(expected_list))):
            instance = instance_list[i]
            expected = expected_list[i]

            result = ForeignKeyParentSerializer(instance=instance).data
            assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_omit_no(self):
        data = {}
        expected_valid = True
        expected = {"id": 3, "nested": None}

        parent = ForeignKeyParentModel.objects.create(id=3)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_omit_yes(self):
        data = {}
        expected_valid = True
        expected = {"id": 5, "nested": {"id": 3, "name": "Max Mustermann"}}

        nested = ForeignKeyNestedModel.objects.create(id=3, name="Max Mustermann")
        parent = ForeignKeyParentModel.objects.create(id=5, nested=nested)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_none_no(self):
        data = {"nested": None}
        expected_valid = True
        expected = {"id": 3, "nested": None}

        parent = ForeignKeyParentModel.objects.create(id=3)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_none_yes(self):
        data = {"nested": None}
        expected_valid = True
        expected = {"id": 5, "nested": None}

        nested = ForeignKeyNestedModel.objects.create(id=3, name="Max Mustermann")
        parent = ForeignKeyParentModel.objects.create(id=5, nested=nested)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_empty_no(self):
        pass

    def test_update_empty_yes(self):
        pass

    def test_update_withoutpk_no(self):
        data = {"nested": {"name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 1, "name": "Max Mustermann"}}

        parent = ForeignKeyParentModel.objects.create(id=3)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withoutpk_yes(self):
        data = {"nested": {"name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 6, "name": "Max Mustermann"}}

        nested = ForeignKeyNestedModel.objects.create(id=5, name="Erika Musterfrau")
        parent = ForeignKeyParentModel.objects.create(id=3, nested=nested)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withnonepk_no(self):
        data = {"nested": {"id": None, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 1, "name": "Max Mustermann"}}

        parent = ForeignKeyParentModel.objects.create(id=3)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withnonepk_yes(self):
        data = {"nested": {"id": None, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 6, "name": "Max Mustermann"}}

        nested = ForeignKeyNestedModel.objects.create(id=5, name="Erika Musterfrau")
        parent = ForeignKeyParentModel.objects.create(id=3, nested=nested)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlypk_no(self):
        data = {"nested": {"id": 5}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        ForeignKeyNestedModel.objects.create(id=5, name="Max Mustermann")
        parent = ForeignKeyParentModel.objects.create(id=3)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlypk_yes(self):
        data = {"nested": {"id": 5}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        ForeignKeyNestedModel.objects.create(id=5, name="Max Mustermann")
        nested = ForeignKeyNestedModel.objects.create(id=7, name="Erika Musterfrau")
        parent = ForeignKeyParentModel.objects.create(id=3, nested=nested)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlysamepk_yes(self):
        data = {"nested": {"id": 5}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        nested = ForeignKeyNestedModel.objects.create(id=5, name="Max Mustermann")
        parent = ForeignKeyParentModel.objects.create(id=3, nested=nested)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withpk_no(self):
        data = {"nested": {"id": 5, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        ForeignKeyNestedModel.objects.create(id=5, name="Erika Musterfrau")
        parent = ForeignKeyParentModel.objects.create(id=3)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withpk_yes(self):
        data = {"nested": {"id": 5, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        ForeignKeyNestedModel.objects.create(id=5, name="Erika Musterfrau")
        nested = ForeignKeyNestedModel.objects.create(id=7, name="Erika Musterfrau")
        parent = ForeignKeyParentModel.objects.create(id=3, nested=nested)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withsamepk_yes(self):
        data = {"nested": {"id": 5, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        nested = ForeignKeyNestedModel.objects.create(id=5, name="Erika Musterfrau")
        parent = ForeignKeyParentModel.objects.create(id=3, nested=nested)
        instance = parent

        serializer = ForeignKeyParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ForeignKeyParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_multiple_no(self):
        data_list = [
            {},  # Omit
            {"nested": None},  # None
            {"nested": {"name": "Max Mustermann"}},  # Without pk
            {"nested": {"id": None, "name": "Erika Musterfrau"}},  # With `None` pk
            {"nested": {"id": 3}},  # Only pk
            {"nested": {"id": 5, "name": "Paul Beispielmann"}},  # With pk
        ]
        expected_valid = True
        expected_list = [
            {"id": 3, "nested": None},
            {"id": 5, "nested": None},
            {"id": 7, "nested": {"id": 6, "name": "Max Mustermann"}},
            {"id": 9, "nested": {"id": 7, "name": "Erika Musterfrau"}},
            {"id": 11, "nested": {"id": 3, "name": "Erna Beispielfrau"}},
            {"id": 13, "nested": {"id": 5, "name": "Paul Beispielmann"}},
        ]

        ForeignKeyNestedModel.objects.create(id=3, name="Erna Beispielfrau")
        ForeignKeyNestedModel.objects.create(id=5, name="John Doe")
        instance_list = [
            ForeignKeyParentModel.objects.create(id=3),
            ForeignKeyParentModel.objects.create(id=5),
            ForeignKeyParentModel.objects.create(id=7),
            ForeignKeyParentModel.objects.create(id=9),
            ForeignKeyParentModel.objects.create(id=11),
            ForeignKeyParentModel.objects.create(id=13),
        ]

        for i in range(len(data_list)):
            data = data_list[i]
            instance = instance_list[i]

            serializer = ForeignKeyParentSerializer(data=data, instance=instance)
            assert serializer.is_valid() == expected_valid, serializer.errors
            instance_list[i] = serializer.save()

        for i in range(max(len(data_list), len(expected_list))):
            instance = instance_list[i]
            expected = expected_list[i]

            result = ForeignKeyParentSerializer(instance=instance).data
            assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_multiple_yes(self):
        data_list = [
            {},  # Omit
            {"nested": None},  # None
            {"nested": {"name": "Max Mustermann"}},  # Without pk
            {"nested": {"id": None, "name": "Erika Musterfrau"}},  # With `None` pk
            {"nested": {"id": 3}},  # Only pk
            {"nested": {"id": 5, "name": "Paul Beispielmann"}},  # With pk
        ]
        expected_valid = True
        expected_list = [
            {"id": 3, "nested": {"id": 7, "name": "Jane Doe"}},
            {"id": 5, "nested": None},
            {"id": 7, "nested": {"id": 18, "name": "Max Mustermann"}},
            {"id": 9, "nested": {"id": 19, "name": "Erika Musterfrau"}},
            {"id": 11, "nested": {"id": 3, "name": "Erna Beispielfrau"}},
            {"id": 13, "nested": {"id": 5, "name": "Paul Beispielmann"}},
        ]

        ForeignKeyNestedModel.objects.create(id=3, name="Erna Beispielfrau")
        ForeignKeyNestedModel.objects.create(id=5, name="John Doe")
        nested_list = [
            ForeignKeyNestedModel.objects.create(id=7, name="Jane Doe"),
            ForeignKeyNestedModel.objects.create(id=9, name="Jane Doe"),
            ForeignKeyNestedModel.objects.create(id=11, name="Jane Doe"),
            ForeignKeyNestedModel.objects.create(id=13, name="Jane Doe"),
            ForeignKeyNestedModel.objects.create(id=15, name="Jane Doe"),
            ForeignKeyNestedModel.objects.create(id=17, name="Jane Doe"),
        ]
        instance_list = [
            ForeignKeyParentModel.objects.create(id=3, nested=nested_list[0]),
            ForeignKeyParentModel.objects.create(id=5, nested=nested_list[1]),
            ForeignKeyParentModel.objects.create(id=7, nested=nested_list[2]),
            ForeignKeyParentModel.objects.create(id=9, nested=nested_list[3]),
            ForeignKeyParentModel.objects.create(id=11, nested=nested_list[4]),
            ForeignKeyParentModel.objects.create(id=13, nested=nested_list[5]),
        ]

        for i in range(len(data_list)):
            data = data_list[i]
            instance = instance_list[i]

            serializer = ForeignKeyParentSerializer(data=data, instance=instance)
            assert serializer.is_valid() == expected_valid, serializer.errors
            instance_list[i] = serializer.save()

        for i in range(max(len(data_list), len(expected_list))):
            instance = instance_list[i]
            expected = expected_list[i]

            result = ForeignKeyParentSerializer(instance=instance).data
            assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
