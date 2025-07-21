from django import test
from django.db import models
from rest_framework.serializers import ModelSerializer

from drf_nested_serializer.serializer import NestedSerializer
from tests.relationships.test_relationship import RelationshipTest


class ThroughNestedModel(models.Model):
    name = models.CharField()


class ThroughParentModel(models.Model):
    nested = models.ManyToManyField(ThroughNestedModel, through="ThroughThroughModel")


class ThroughThroughModel(models.Model):
    nested = models.ForeignKey(ThroughNestedModel, on_delete=models.CASCADE)
    parent = models.ForeignKey(
        ThroughParentModel, on_delete=models.CASCADE, related_name="through"
    )
    extra = models.CharField()


class ThroughThroughSerializer(ModelSerializer):
    class Meta:
        model = ThroughThroughModel
        fields = ("id", "nested", "extra")


class ThroughParentSerializer(NestedSerializer):
    nested = ThroughThroughSerializer(
        many=True, required=False, allow_empty=True, source="through"
    )

    class Meta:
        model = ThroughParentModel
        fields = ("id", "nested")


class ThroughTest(RelationshipTest, test.TestCase):
    def test_create_omit_no(self):
        data = {}
        expected_valid = True
        expected = {"id": 1, "through": []}

        serializer = ThroughParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_none_no(self):
        pass

    def test_create_empty_no(self):
        data = {"through": []}
        expected_valid = True
        expected = {"id": 1, "through": []}

        serializer = ThroughParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_withoutpk_no(self):
        data = {"through": [{"nested": 1, "extra": "Foo"}]}
        expected_valid = True
        expected = {
            "id": 1,
            "through": [{"id": 1, "nested": 1, "extra": "Foo"}],
        }

        ThroughNestedModel.objects.create(id=1, name="Max Mustermann")

        serializer = ThroughParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_withnonepk_no(self):
        data = {
            "through": [
                {"id": None, "nested": 1, "extra": "Foo 1"},
                {"id": None, "nested": 1, "extra": "Foo 2"},
            ]
        }
        expected_valid = True
        expected = {
            "id": 1,
            "through": [
                {"id": 1, "nested": 1, "extra": "Foo 1"},
                {"id": 2, "nested": 1, "extra": "Foo 2"},
            ],
        }

        ThroughNestedModel.objects.create(name="Max Mustermann")

        serializer = ThroughParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_onlypk_no(self):
        pass

    def test_create_withpk_no(self):
        pass

    def test_create_multiple_no(self):
        pass

    def test_update_omit_no(self):
        data = {}
        expected_valid = True
        expected = {"id": 3, "through": []}

        parent = ThroughParentModel.objects.create(id=3)
        instance = parent

        serializer = ThroughParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_omit_yes(self):
        data = {}
        expected_valid = True
        expected = {"id": 5, "through": [{"id": 3, "nested": 3, "extra": "Foo 1"}]}

        nested = ThroughNestedModel.objects.create(id=3, name="Max Mustermann")
        parent = ThroughParentModel.objects.create(id=5)
        ThroughThroughModel.objects.create(
            id=3, nested=nested, parent=parent, extra="Foo 1"
        )
        instance = parent

        serializer = ThroughParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_none_no(self):
        pass

    def test_update_none_yes(self):
        pass

    def test_update_empty_no(self):
        data = {"through": []}
        expected_valid = True
        expected = {"id": 3, "through": []}

        parent = ThroughParentModel.objects.create(id=3)
        ThroughNestedModel.objects.create(id=5)
        instance = parent

        serializer = ThroughParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_empty_yes(self):
        data = {"through": []}
        expected_valid = True
        expected = {"id": 3, "through": []}

        nested = ThroughNestedModel.objects.create(id=5, name="Max Mustermann")
        parent = ThroughParentModel.objects.create(id=3)
        ThroughThroughModel.objects.create(parent=parent, nested=nested, extra="Foo 1")
        instance = parent

        serializer = ThroughParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withoutpk_no(self):
        data = {"through": [{"nested": 5, "extra": "Foo 1"}]}
        expected_valid = True
        expected = {"id": 3, "through": [{"id": 1, "nested": 5, "extra": "Foo 1"}]}

        parent = ThroughParentModel.objects.create(id=3)
        ThroughNestedModel.objects.create(id=5)
        instance = parent

        serializer = ThroughParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withoutpk_yes(self):
        data = {"through": [{"nested": 5, "extra": "Foo 1"}]}
        expected_valid = True
        expected = {"id": 3, "through": [{"id": 8, "nested": 5, "extra": "Foo 1"}]}

        parent = ThroughParentModel.objects.create(id=3)
        nested = ThroughNestedModel.objects.create(id=5, name="Erika Musterfrau")
        ThroughThroughModel.objects.create(
            id=7, parent=parent, nested=nested, extra="Foo 2"
        )
        instance = parent

        serializer = ThroughParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withnonepk_no(self):
        data = {"through": [{"id": None, "nested": 5, "extra": "Foo 1"}]}
        expected_valid = True
        expected = {"id": 3, "through": [{"id": 1, "nested": 5, "extra": "Foo 1"}]}

        parent = ThroughParentModel.objects.create(id=3)
        ThroughNestedModel.objects.create(id=5)
        instance = parent

        serializer = ThroughParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withnonepk_yes(self):
        data = {"through": [{"id": None, "nested": 5, "extra": "Foo 1"}]}
        expected_valid = True
        expected = {"id": 3, "through": [{"id": 8, "nested": 5, "extra": "Foo 1"}]}

        parent = ThroughParentModel.objects.create(id=3)
        nested = ThroughNestedModel.objects.create(id=5, name="Erika Musterfrau")
        ThroughThroughModel.objects.create(
            id=7, parent=parent, nested=nested, extra="Foo 2"
        )
        instance = parent

        serializer = ThroughParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlypk_no(self):
        pass

    def test_update_onlypk_yes(self):
        pass

    def test_update_onlysamepk_yes(self):
        pass

    def test_update_withpk_no(self):
        pass

    def test_update_withpk_yes(self):
        pass

    def test_update_withsamepk_yes(self):
        data = {"through": [{"id": 7, "extra": "Foo 2"}]}
        expected_valid = True
        expected = {"id": 3, "through": [{"id": 7, "nested": 5, "extra": "Foo 2"}]}

        parent = ThroughParentModel.objects.create(id=3)
        nested = ThroughNestedModel.objects.create(id=5, name="Erika Musterfrau")
        ThroughThroughModel.objects.create(
            id=7, parent=parent, nested=nested, extra="Foo 1"
        )
        instance = parent

        serializer = ThroughParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ThroughParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_multiple_no(self):
        # TODO
        return

    def test_update_multiple_yes(self):
        # TODO
        return
