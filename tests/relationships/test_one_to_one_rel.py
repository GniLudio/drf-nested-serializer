from django import test
from django.db import models
from rest_framework.serializers import ModelSerializer

from drf_nested_serializer.serializer import NestedSerializer
from tests.relationships.test_relationship import RelationshipTest


class OneToOneRelParentModel(models.Model):
    pass


class OneToOneRelNestedModel(models.Model):
    name = models.CharField()
    parent = models.OneToOneField(
        OneToOneRelParentModel,
        on_delete=models.CASCADE,
        null=True,
        related_name="nested",
    )


class OneToOneRelNestedSerializer(ModelSerializer):
    class Meta:
        model = OneToOneRelNestedModel
        fields = ("id", "name")


class OneToOneRelParentSerializer(NestedSerializer):
    nested = OneToOneRelNestedSerializer(required=False, allow_null=True)

    class Meta:
        model = OneToOneRelParentModel
        fields = ("id", "nested")


class OneToOneRelTest(RelationshipTest, test.TestCase):
    def test_create_omit_no(self):
        data = {}
        expected_valid = True
        expected = {"id": 1, "nested": None}

        serializer = OneToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_none_no(self):
        data = {"nested": None}
        expected_valid = True
        expected = {"id": 1, "nested": None}

        serializer = OneToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_empty_no(self):
        pass

    def test_create_withoutpk_no(self):
        data = {"nested": {"name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 1, "nested": {"id": 1, "name": "Max Mustermann"}}

        serializer = OneToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_withnonepk_no(self):
        data = {"nested": {"id": None, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 1, "nested": {"id": 1, "name": "Max Mustermann"}}

        serializer = OneToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_onlypk_no(self):
        data = {"nested": {"id": 3}}
        expected_valid = True
        expected = {"id": 1, "nested": {"id": 3, "name": "Max Mustermann"}}

        OneToOneRelNestedModel.objects.create(id=3, name="Max Mustermann")

        serializer = OneToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_withpk_no(self):
        data = {"nested": {"id": 3, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 1, "nested": {"id": 3, "name": "Max Mustermann"}}

        OneToOneRelNestedModel.objects.create(id=3, name="Erika Musterfrau")

        serializer = OneToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
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

        OneToOneRelNestedModel.objects.create(id=3, name="Erna Beispielfrau")
        OneToOneRelNestedModel.objects.create(id=5, name="John Doe")

        instance_list = []
        for i in range(len(data_list)):
            data = data_list[i]

            serializer = OneToOneRelParentSerializer(data=data)
            assert serializer.is_valid() == expected_valid, serializer.errors
            instance_list.append(serializer.save())

        for i in range(max(len(data_list), len(expected_list))):
            instance = instance_list[i]
            expected = expected_list[i]

            result = OneToOneRelParentSerializer(instance=instance).data
            assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_omit_no(self):
        data = {}
        expected_valid = True
        expected = {"id": 3, "nested": None}

        parent = OneToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_omit_yes(self):
        data = {}
        expected_valid = True
        expected = {"id": 5, "nested": {"id": 3, "name": "Max Mustermann"}}

        parent = OneToOneRelParentModel.objects.create(id=5)
        OneToOneRelNestedModel.objects.create(
            id=3, name="Max Mustermann", parent=parent
        )
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_none_no(self):
        data = {"nested": None}
        expected_valid = True
        expected = {"id": 3, "nested": None}

        parent = OneToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_none_yes(self):
        data = {"nested": None}
        expected_valid = True
        expected = {"id": 5, "nested": None}

        parent = OneToOneRelParentModel.objects.create(id=5)
        OneToOneRelNestedModel.objects.create(
            id=3, name="Max Mustermann", parent=parent
        )
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_empty_no(self):
        pass

    def test_update_empty_yes(self):
        pass

    def test_update_withoutpk_no(self):
        data = {"nested": {"name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 1, "name": "Max Mustermann"}}

        parent = OneToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withoutpk_yes(self):
        data = {"nested": {"name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 6, "name": "Max Mustermann"}}

        parent = OneToOneRelParentModel.objects.create(id=3)
        OneToOneRelNestedModel.objects.create(
            id=5, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withnonepk_no(self):
        data = {"nested": {"id": None, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 1, "name": "Max Mustermann"}}

        parent = OneToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withnonepk_yes(self):
        data = {"nested": {"id": None, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 6, "name": "Max Mustermann"}}

        parent = OneToOneRelParentModel.objects.create(id=3)
        OneToOneRelNestedModel.objects.create(
            id=5, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlypk_no(self):
        data = {"nested": {"id": 5}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        OneToOneRelNestedModel.objects.create(id=5, name="Max Mustermann")
        parent = OneToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlypk_yes(self):
        data = {"nested": {"id": 5}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        OneToOneRelNestedModel.objects.create(id=5, name="Max Mustermann")
        parent = OneToOneRelParentModel.objects.create(id=3)
        OneToOneRelNestedModel.objects.create(
            id=7, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlysamepk_yes(self):
        data = {"nested": {"id": 5}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        parent = OneToOneRelParentModel.objects.create(id=3)
        OneToOneRelNestedModel.objects.create(
            id=5, name="Max Mustermann", parent=parent
        )
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withpk_no(self):
        data = {"nested": {"id": 5, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        OneToOneRelNestedModel.objects.create(id=5, name="Erika Musterfrau")
        parent = OneToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withpk_yes(self):
        data = {"nested": {"id": 5, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        OneToOneRelNestedModel.objects.create(id=5, name="Erika Musterfrau")
        parent = OneToOneRelParentModel.objects.create(id=3)
        OneToOneRelNestedModel.objects.create(
            id=7, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withsamepk_yes(self):
        data = {"nested": {"id": 5, "name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 3, "nested": {"id": 5, "name": "Max Mustermann"}}

        parent = OneToOneRelParentModel.objects.create(id=3)
        OneToOneRelNestedModel.objects.create(
            id=5, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = OneToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = OneToOneRelParentSerializer(instance=instance).data
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

        OneToOneRelNestedModel.objects.create(id=3, name="Erna Beispielfrau")
        OneToOneRelNestedModel.objects.create(id=5, name="John Doe")
        instance_list = [
            OneToOneRelParentModel.objects.create(id=3),
            OneToOneRelParentModel.objects.create(id=5),
            OneToOneRelParentModel.objects.create(id=7),
            OneToOneRelParentModel.objects.create(id=9),
            OneToOneRelParentModel.objects.create(id=11),
            OneToOneRelParentModel.objects.create(id=13),
        ]

        for i in range(len(data_list)):
            data = data_list[i]
            instance = instance_list[i]

            serializer = OneToOneRelParentSerializer(data=data, instance=instance)
            assert serializer.is_valid() == expected_valid, serializer.errors
            instance_list[i] = serializer.save()

        for i in range(max(len(data_list), len(expected_list))):
            instance = instance_list[i]
            expected = expected_list[i]

            result = OneToOneRelParentSerializer(instance=instance).data
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

        OneToOneRelNestedModel.objects.create(id=3, name="Erna Beispielfrau")
        OneToOneRelNestedModel.objects.create(id=5, name="John Doe")
        instance_list = [
            OneToOneRelParentModel.objects.create(id=3),
            OneToOneRelParentModel.objects.create(id=5),
            OneToOneRelParentModel.objects.create(id=7),
            OneToOneRelParentModel.objects.create(id=9),
            OneToOneRelParentModel.objects.create(id=11),
            OneToOneRelParentModel.objects.create(id=13),
        ]
        OneToOneRelNestedModel.objects.create(
            id=7, name="Jane Doe", parent=instance_list[0]
        )
        OneToOneRelNestedModel.objects.create(
            id=9, name="Jane Doe", parent=instance_list[1]
        )
        OneToOneRelNestedModel.objects.create(
            id=11, name="Jane Doe", parent=instance_list[2]
        )
        OneToOneRelNestedModel.objects.create(
            id=13, name="Jane Doe", parent=instance_list[3]
        )
        OneToOneRelNestedModel.objects.create(
            id=15, name="Jane Doe", parent=instance_list[4]
        )
        OneToOneRelNestedModel.objects.create(
            id=17, name="Jane Doe", parent=instance_list[5]
        )

        for i in range(len(data_list)):
            data = data_list[i]
            instance = instance_list[i]

            serializer = OneToOneRelParentSerializer(data=data, instance=instance)
            assert serializer.is_valid() == expected_valid, serializer.errors
            instance_list[i] = serializer.save()

        for i in range(max(len(data_list), len(expected_list))):
            instance = instance_list[i]
            expected = expected_list[i]

            result = OneToOneRelParentSerializer(instance=instance).data
            assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
