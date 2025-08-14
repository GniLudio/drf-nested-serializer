from django.db import models
from django.test import TestCase
from rest_framework.serializers import (
    ListSerializer,
    ModelSerializer,
    PrimaryKeyRelatedField,
    ManyRelatedField,
)

from drf_nested_model_serializer.serializer import NestedModelSerializer


class AllNestedModel(models.Model):
    name = models.CharField()


class AllParentModel(models.Model):
    o2o = models.OneToOneField(
        AllNestedModel, on_delete=models.CASCADE, related_name="o2o_parent"
    )
    fk = models.ForeignKey(
        AllNestedModel, on_delete=models.CASCADE, related_name="fk_parent"
    )
    m2m = models.ManyToManyField(AllNestedModel, related_name="m2m_parent")
    name = models.CharField()


class AllNestedO2ORelModel(models.Model):
    parent = models.OneToOneField(
        AllParentModel, on_delete=models.CASCADE, related_name="o2o_rel"
    )
    name = models.CharField()


class AllNestedFKRelModel(models.Model):
    parent = models.ForeignKey(
        AllParentModel, on_delete=models.CASCADE, related_name="fk_rel"
    )
    name = models.CharField()


class AllNestedM2MRelModel(models.Model):
    parent = models.ManyToManyField(AllParentModel, related_name="m2m_rel")
    name = models.CharField()


class AllNestedThroughModel(models.Model):
    parent = models.ForeignKey(
        AllParentModel, on_delete=models.CASCADE, related_name="fk_rel_through"
    )
    nested = models.ForeignKey(
        AllNestedModel, on_delete=models.CASCADE, related_name="fk_rel_through"
    )
    name = models.CharField()


class AllNestedSerializer(ModelSerializer):
    class Meta:
        model = AllNestedModel
        fields = "__all__"


class AllNestedO2ORelSerializer(ModelSerializer):
    class Meta:
        model = AllNestedO2ORelModel
        fields = "__all__"


class AllNestedFKRelSerializer(ModelSerializer):
    class Meta:
        model = AllNestedFKRelModel
        fields = "__all__"


class AllNestedM2MRelSerializer(ModelSerializer):
    class Meta:
        model = AllNestedM2MRelModel
        fields = "__all__"


class AllNestedThroughSerializer(ModelSerializer):
    class Meta:
        model = AllNestedThroughModel
        fields = "__all__"


class AllParentSerializer(NestedModelSerializer):
    o2o = AllNestedSerializer()
    fk = AllNestedSerializer()
    m2m = AllNestedSerializer(many=True)
    o2o_rel = AllNestedO2ORelSerializer()
    fk_rel = AllNestedFKRelSerializer(many=True)
    m2m_rel = AllNestedM2MRelSerializer(many=True)
    fk_rel_through = AllNestedThroughSerializer(many=True)

    class Meta:
        model = AllParentModel
        fields = "__all__"


class AllTest(TestCase):
    def test(self):
        serializer = AllParentSerializer()

        assert isinstance(serializer, AllParentSerializer)
        expected = {
            "id",
            "o2o",
            "fk",
            "m2m",
            "name",
            "o2o_rel",
            "fk_rel",
            "m2m_rel",
            "fk_rel_through",
        }
        result = dict(serializer.fields).keys()
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

        expected = {"id", "name"}
        assert isinstance(serializer.fields["o2o"], AllNestedSerializer)
        result = dict(serializer.fields["o2o"].fields).keys()
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

        expected = {"id", "name"}
        assert isinstance(serializer.fields["fk"], AllNestedSerializer)
        result = dict(serializer.fields["fk"].fields).keys()
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

        expected = {"id", "name"}
        assert isinstance(serializer.fields["m2m"], ListSerializer)
        assert isinstance(serializer.fields["m2m"].child, AllNestedSerializer)
        result = dict(serializer.fields["m2m"].child.fields).keys()
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

        expected = {"id", "name", "parent"}
        assert isinstance(serializer.fields["o2o_rel"], AllNestedO2ORelSerializer)
        result = dict(serializer.fields["o2o_rel"].fields).keys()
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
        assert isinstance(
            serializer.fields["o2o_rel"].fields["parent"], PrimaryKeyRelatedField
        )
        assert serializer.fields["o2o_rel"].fields["parent"].read_only
        assert not serializer.fields["o2o_rel"].fields["parent"].write_only

        expected = {"id", "name", "parent"}
        assert isinstance(serializer.fields["fk_rel"], ListSerializer)
        assert isinstance(serializer.fields["fk_rel"].child, AllNestedFKRelSerializer)
        result = dict(serializer.fields["fk_rel"].child.fields).keys()
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
        assert isinstance(
            serializer.fields["fk_rel"].child.fields["parent"], PrimaryKeyRelatedField
        )
        assert serializer.fields["fk_rel"].child.fields["parent"].read_only
        assert not serializer.fields["fk_rel"].child.fields["parent"].write_only

        expected = {"id", "name", "parent"}
        assert isinstance(serializer.fields["m2m_rel"], ListSerializer)
        assert isinstance(serializer.fields["m2m_rel"].child, AllNestedM2MRelSerializer)
        result = dict(serializer.fields["m2m_rel"].child.fields).keys()
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
        assert isinstance(
            serializer.fields["m2m_rel"].child.fields["parent"], ManyRelatedField
        )
        assert serializer.fields["m2m_rel"].child.fields["parent"].read_only
        assert not serializer.fields["m2m_rel"].child.fields["parent"].write_only

        expected = {"id", "name", "parent", "nested"}
        assert isinstance(serializer.fields["fk_rel_through"], ListSerializer)
        assert isinstance(
            serializer.fields["fk_rel_through"].child, AllNestedThroughSerializer
        )
        result = dict(serializer.fields["fk_rel_through"].child.fields).keys()
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
        assert serializer.fields["fk_rel_through"].child.fields["parent"].read_only
        assert not serializer.fields["fk_rel_through"].child.fields["parent"].write_only
