"""from django.test import TestCase

from drf_nested_serializer import ParentSerializer
from drf_nested_serializer import NestedSerializer

from django.db import models


# Non-Nullable Models and Serializers
class NonNullableO2ONestedModel(models.Model):
    pass


class NonNullableFKNestedModel(models.Model):
    pass


class NonNullableM2MNestedModel(models.Model):
    pass


class NonNullableParentModel(models.Model):
    foreign_key = models.ForeignKey(
        NonNullableFKNestedModel,
        null=False,
        related_name="+",
        on_delete=models.CASCADE,
    )
    one_to_one = models.OneToOneField(
        NonNullableO2ONestedModel,
        null=False,
        related_name="+",
        on_delete=models.CASCADE,
    )
    many_to_many = models.ManyToManyField(NonNullableM2MNestedModel)


class NonNullableO2ORNestedModel(models.Model):
    one_to_one = models.OneToOneField(
        NonNullableParentModel,
        null=False,
        related_name="one_to_one_rel",
        on_delete=models.CASCADE,
    )


class NonNullableM2ORNestedModel(models.Model):
    foreign_key = models.ForeignKey(
        NonNullableParentModel,
        related_name="many_to_one_rel",
        on_delete=models.CASCADE,
    )


class NonNullableM2MRNestedModel(models.Model):
    many_to_many = models.ManyToManyField(
        NonNullableParentModel,
        related_name="many_to_many_rel",
    )


class NonNullableO2ONestedSerializer(NestedSerializer):
    class Meta:
        model = NonNullableO2ONestedModel
        fields = ("id",)


class NonNullableFKNestedSerializer(NestedSerializer):
    class Meta:
        model = NonNullableFKNestedModel
        fields = ("id",)


class NonNullableM2MNestedSerializer(NestedSerializer):
    class Meta:
        model = NonNullableM2MNestedModel
        fields = ("id",)


class NonNullableO2ORNestedSerializer(NestedSerializer):
    class Meta:
        model = NonNullableO2ORNestedModel
        fields = ("id",)


class NonNullableM2ORNestedSerializer(NestedSerializer):
    class Meta:
        model = NonNullableM2ORNestedModel
        fields = ("id",)


class NonNullableM2MRNestedSerializer(NestedSerializer):
    class Meta:
        model = NonNullableM2MRNestedModel
        fields = ("id",)


class NonNullableParentSerializer(ParentSerializer):
    one_to_one = NonNullableO2ONestedSerializer()
    foreign_key = NonNullableFKNestedSerializer()
    many_to_many = NonNullableM2MNestedSerializer(many=True, allow_empty=False)
    one_to_one_rel = NonNullableO2ORNestedSerializer()
    many_to_one_rel = NonNullableM2ORNestedSerializer(many=True, allow_empty=False)
    many_to_many_rel = NonNullableM2MRNestedSerializer(many=True, allow_empty=False)

    class Meta:
        model = NonNullableParentModel
        fields = (
            "id",
            "one_to_one",
            "foreign_key",
            "many_to_many",
            "one_to_one_rel",
            "many_to_one_rel",
            "many_to_many_rel",
        )


class NullableTest(TestCase):
    def test_non_nullable(self):
        data = {
            "foreign_key": {},
            "many_to_one_rel": [{}, {}, {}],
            "one_to_one": {},
            "one_to_one_rel": {},
            "many_to_many": [{}, {}, {}],
            "many_to_many_rel": [{}, {}, {}],
        }
        expected_valid = True
        expected = {
            "id": 1,
            "foreign_key": {"id": 1},
            "many_to_one_rel": [{"id": 1}, {"id": 2}, {"id": 3}],
            "one_to_one": {"id": 1},
            "one_to_one_rel": {"id": 1},
            "many_to_many": [{"id": 1}, {"id": 2}, {"id": 3}],
            "many_to_many_rel": [{"id": 1}, {"id": 2}, {"id": 3}],
        }

        serializer = NonNullableParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = NonNullableParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
"""
