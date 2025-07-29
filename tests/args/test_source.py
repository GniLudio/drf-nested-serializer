from django.test import TestCase

from django.db import models

from drf_nested_model_serializer.serializer import NestedModelSerializer
from rest_framework.serializers import ModelSerializer


class SourceOneToOneModel(models.Model):
    name = models.CharField()


class SourceOneToOneSerializer(ModelSerializer):
    class Meta:
        model = SourceOneToOneModel
        fields = ("id", "name")


class SourceForeignKeyModel(models.Model):
    name = models.CharField()


class SourceForeignKeySerializer(ModelSerializer):
    class Meta:
        model = SourceForeignKeyModel
        fields = ("id", "name")


class SourceManyToManyModel(models.Model):
    name = models.CharField()


class SourceManyToManySerializer(ModelSerializer):
    class Meta:
        model = SourceManyToManyModel
        fields = ("id", "name")


class SourceParentModel(models.Model):
    nested_1 = models.OneToOneField(SourceOneToOneModel, on_delete=models.CASCADE)
    nested_2 = models.ForeignKey(SourceForeignKeyModel, on_delete=models.CASCADE)
    nested_3 = models.ManyToManyField(SourceManyToManyModel)


class SourceOneToOneRelModel(models.Model):
    name = models.CharField()
    parent = models.OneToOneField(
        SourceParentModel, on_delete=models.CASCADE, related_name="nested_4"
    )


class SourceOneToOneRelSerializer(ModelSerializer):
    class Meta:
        model = SourceOneToOneRelModel
        fields = ("id", "name")


class SourceManyToOneRelModel(models.Model):
    name = models.CharField()
    parent = models.ForeignKey(
        SourceParentModel, on_delete=models.CASCADE, related_name="nested_5"
    )


class SourceManyToOneRelSerializer(ModelSerializer):
    class Meta:
        model = SourceManyToOneRelModel
        fields = ("id", "name")


class SourceManyToManyRelModel(models.Model):
    name = models.CharField()
    parent = models.ManyToManyField(SourceParentModel, related_name="nested_6")


class SourceManyToManyRelSerializer(ModelSerializer):
    class Meta:
        model = SourceManyToManyRelModel
        fields = ("id", "name")


class SourceParentSerializer(NestedModelSerializer):
    other_1 = SourceOneToOneSerializer(source="nested_1")
    other_2 = SourceForeignKeySerializer(source="nested_2")
    other_3 = SourceManyToManySerializer(source="nested_3", many=True)
    other_4 = SourceOneToOneRelSerializer(source="nested_4")
    other_5 = SourceManyToOneRelSerializer(source="nested_5", many=True)
    other_6 = SourceManyToManyRelSerializer(source="nested_6", many=True)

    class Meta:
        model = SourceParentModel
        fields = (
            "id",
            "other_1",
            "other_2",
            "other_3",
            "other_4",
            "other_5",
            "other_6",
        )


class SourceTest(TestCase):
    def test(self):
        data = {
            "other_1": {"name": "Max Mustermann"},
            "other_2": {"name": "Erika Musterfrau"},
            "other_3": [{"name": "Paul Beispielmann"}],
            "other_4": {"name": "Erika Beispielfrau"},
            "other_5": [{"name": "John Doe"}],
            "other_6": [{"name": "Jane Doe"}],
        }
        expected_valid = True
        expected = {
            "id": 1,
            "other_1": {"id": 1, "name": "Max Mustermann"},
            "other_2": {"id": 1, "name": "Erika Musterfrau"},
            "other_3": [{"id": 1, "name": "Paul Beispielmann"}],
            "other_4": {"id": 1, "name": "Erika Beispielfrau"},
            "other_5": [{"id": 1, "name": "John Doe"}],
            "other_6": [{"id": 1, "name": "Jane Doe"}],
        }

        serializer = SourceParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = SourceParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
