"""from django.test import TestCase
from django.db import models

from drf_nested_serializer import ParentSerializer
from drf_nested_serializer import NestedModelSerializer


class InvalidEmptyNestedModel(models.Model):
    pass


class InvalidEmptyNestedModelSerializer(NestedModelSerializer):
    class Meta:
        model = InvalidEmptyNestedModel
        fields = ("id",)


class InvalidPKParentModel(models.Model):
    nested = models.OneToOneField(InvalidEmptyNestedModel, on_delete=models.CASCADE)


class InvalidPKParentSerializer(ParentSerializer):
    nested = InvalidEmptyNestedModelSerializer()

    class Meta:
        model = InvalidPKParentModel
        fields = ("id", "nested")


class ValidationTest(TestCase):
    def test_invalid_pk(self):
        data = {"nested": {"id": 1}}
        serializer = InvalidPKParentSerializer(data=data)
        assert not serializer.is_valid()

        nested = InvalidEmptyNestedModel.objects.create(id=3)
        InvalidPKParentModel.objects.create(nested=nested)

        data = {"nested": {"id": 3}}
        serializer = InvalidPKParentSerializer(data=data)
        assert not serializer.is_valid()

    def test_invalid_type(self):
        pass

    def test_invalid_field_type(self):
        pass

    def test_invalid_field_value(self):
        pass

    def test_invalid_create_unique(self):
        pass
"""
