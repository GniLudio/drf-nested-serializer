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


class ArgTest(TestCase):
    def test_required(self):
        pass

    def test_allow_null(self):
        pass

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

    def test_delete_on_remove(self):
        pass
