from django.db import models
from django.test import TestCase

from rest_framework.serializers import ModelSerializer
from drf_nested_model_serializer.serializer import NestedModelSerializer


class NestingNested1Model(models.Model):
    name = models.CharField()


class NestingNested2Model(models.Model):
    one_to_one = models.OneToOneField(
        NestingNested1Model, on_delete=models.CASCADE, related_name="+"
    )


class NestingNested3Model(models.Model):
    foreign_key = models.ForeignKey(
        NestingNested2Model, on_delete=models.CASCADE, related_name="+"
    )


class NestingNested4Model(models.Model):
    many_to_many = models.ManyToManyField(NestingNested3Model, related_name="+")
    parent = models.OneToOneField(
        "NestingNested5Model", on_delete=models.CASCADE, related_name="one_to_one_rel"
    )


class NestingNested5Model(models.Model):
    # one_to_one_rel = models.OneToOneRel(NestingNested4Model, related_name="parent")
    parent = models.ForeignKey(
        "NestingNested6Model", related_name="many_to_one_rel", on_delete=models.CASCADE
    )


class NestingNested6Model(models.Model):
    # many_to_one_rel = models.ManyToOneRel(NestingNested5Model, related_name="parent")
    parent = models.ManyToManyField(
        "NestingNested7Model", related_name="many_to_many_rel"
    )


class NestingNested7Model(models.Model):
    # many_to_many_rel = models.ManyToManyRel(NestingNested6Model, related_name="parent")
    pass


class NestingNested1Serializer(ModelSerializer):
    class Meta:
        model = NestingNested1Model
        fields = ("id", "name")


class NestingNested2Serializer(NestedModelSerializer):
    one_to_one = NestingNested1Serializer()

    class Meta:
        model = NestingNested2Model
        fields = ("id", "one_to_one")


class NestingNested3Serializer(NestedModelSerializer):
    foreign_key = NestingNested2Serializer()

    class Meta:
        model = NestingNested3Model
        fields = ("id", "foreign_key")


class NestingNested4Serializer(NestedModelSerializer):
    many_to_many = NestingNested3Serializer(many=True)

    class Meta:
        model = NestingNested4Model
        fields = ("id", "many_to_many")


class NestingNested5Serializer(NestedModelSerializer):
    one_to_one_rel = NestingNested4Serializer()

    class Meta:
        model = NestingNested5Model
        fields = ("id", "one_to_one_rel")


class NestingNested6Serializer(NestedModelSerializer):
    many_to_one_rel = NestingNested5Serializer(many=True)

    class Meta:
        model = NestingNested6Model
        fields = ("id", "many_to_one_rel")


class NestingParentSerializer(NestedModelSerializer):
    many_to_many_rel = NestingNested6Serializer(many=True)

    class Meta:
        model = NestingNested7Model
        fields = ("id", "many_to_many_rel")


class NestingTest(TestCase):
    def test_create(self):
        data = {
            "many_to_many_rel": [
                {
                    "many_to_one_rel": [
                        {
                            "one_to_one_rel": {
                                "many_to_many": [
                                    {
                                        "foreign_key": {
                                            "one_to_one": {
                                                "name": "Max Mustermann",
                                            }
                                        }
                                    },
                                ],
                            }
                        },
                    ]
                },
            ]
        }
        expected_valid = True
        expected = {
            "id": 1,
            "many_to_many_rel": [
                {
                    "id": 1,
                    "many_to_one_rel": [
                        {
                            "id": 1,
                            "one_to_one_rel": {
                                "id": 1,
                                "many_to_many": [
                                    {
                                        "id": 1,
                                        "foreign_key": {
                                            "id": 1,
                                            "one_to_one": {
                                                "id": 1,
                                                "name": "Max Mustermann",
                                            },
                                        },
                                    },
                                ],
                            },
                        },
                    ],
                },
            ],
        }

        serializer = NestingParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = NestingParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
