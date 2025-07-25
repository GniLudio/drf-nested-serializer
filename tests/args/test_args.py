from django.test import TestCase
from django.db import models

from rest_framework.serializers import ModelSerializer

from drf_nested_serializer.serializer import NestedSerializer


class ArgSourceNestedModel(models.Model):
    name = models.CharField()


class ArgSourceParentModel(models.Model):
    nested = models.ForeignKey(ArgSourceNestedModel, on_delete=models.CASCADE)


class ArgSourceNestedSerializer(ModelSerializer):
    class Meta:
        model = ArgSourceNestedModel
        fields = ("id", "name")


class ArgSourceParentSerializer(NestedSerializer):
    foo = ArgSourceNestedSerializer(source="nested")

    class Meta:
        model = ArgSourceParentModel
        fields = ("id", "foo")


class RequiredNestedModel(models.Model):
    pass


class RequiredParentModel(models.Model):
    nested = models.ForeignKey(RequiredNestedModel, on_delete=models.CASCADE)


class RequiredNestedSerializer(ModelSerializer):
    class Meta:
        model = RequiredNestedModel
        fields = ("id",)


class RequiredParentSerializer(NestedSerializer):
    nested = RequiredNestedSerializer(required=True)

    class Meta:
        model = RequiredParentModel
        fields = ("id", "nested")


class NotRequiredParentSerializer(NestedSerializer):
    nested = RequiredNestedSerializer(required=False)

    class Meta:
        model = RequiredParentModel
        fields = ("id", "nested")


class AllowNullNestedModel(models.Model):
    pass


class AllowNullParentModel(models.Model):
    nested = models.ForeignKey(AllowNullNestedModel, on_delete=models.CASCADE)


class AllowNullNestedSerializer(ModelSerializer):
    class Meta:
        model = AllowNullNestedModel
        fields = ("id",)


class ArgTest(TestCase):
    def test_required(self):
        data = {}
        expected_valid = False
        serializer = RequiredParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors

        data = {}
        expected_valid = True
        serializer = NotRequiredParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors

    def test_allow_empty(self):
        pass

    def test_write_only(self):
        pass

    def test_partial(self):
        pass

    def test_source(self):
        data = {"foo": {"name": "Max Mustermann"}}
        expected_valid = True
        expected = {"id": 1, "foo": {"id": 1, "name": "Max Mustermann"}}

        serializer = ArgSourceParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ArgSourceParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
