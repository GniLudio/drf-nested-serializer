from functools import cached_property
from typing import Sequence
from rest_framework.fields import empty
from rest_framework.serializers import (
    ModelSerializer,
    ListSerializer,
    PrimaryKeyRelatedField,
)
from rest_framework.utils import model_meta
from django.db import models

INCLUDE_FIELD = "nested_include"
EXCLUDE_FIELD = "nested_exclude"
ALL_FIELDS = "__all__"


class NestedModelSerializer(ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._add_primary_key_fields()
        self._make_related_field_read_only()

    def create(self, validated_data):
        disabled_serializers = self._handle_forward_nested(validated_data)
        reverse_data = self._pop_reverse_data(validated_data)
        instance = super().create(validated_data)
        self._reactivate_serializers(disabled_serializers)
        self._handle_reverse_nested(instance, reverse_data)
        instance.refresh_from_db()
        return instance

    def update(self, instance, validated_data):
        disabled_serializers = self._handle_forward_nested(validated_data)
        reverse_data = self._pop_reverse_data(validated_data)
        instance = super().update(instance, validated_data)
        self._reactivate_serializers(disabled_serializers)
        self._handle_reverse_nested(instance, reverse_data)
        instance.refresh_from_db()
        return instance

    def _add_primary_key_fields(self):
        for field in self._nested_serializers.values():
            nested_pk_name = get_pk_name(field)
            if isinstance(field, ListSerializer):
                field = field.child
            field.fields[nested_pk_name] = PrimaryKeyRelatedField(
                queryset=field.Meta.model.objects.all(), required=False, allow_null=True
            )
            self._override_run_validation(field)

    def _make_related_field_read_only(self):
        for name, serializer in self._nested_serializers_reverse.items():
            if isinstance(serializer, ListSerializer):
                serializer = serializer.child
            model_field: models.Field = self.Meta.model._meta.get_field(name)
            related_name = model_field.field.name
            if related_name in serializer.fields:
                serializer.fields[related_name].write_only = False
                serializer.fields[related_name].read_only = True

    def _override_run_validation(self, field):
        original = field.run_validation
        pk_name = get_pk_name(field)

        def run_validation(data=empty):
            original_required = {}
            if isinstance(data, dict) and data.get(pk_name, None) is not None:
                field.partial = True
                for name, nested_field in field.fields.items():
                    original_required[name] = nested_field.required
                    nested_field.required = False
            result = original(data)
            for name, required in original_required.items():
                field.fields[name].required = required
            return result

        field.run_validation = run_validation

    def _handle_forward_nested(self, validated_data):
        result = self._update_or_create_nested(
            validated_data, self._nested_serializers_forward
        )
        for name, value in result.items():
            validated_data[name] = value

        disabled_serializers = []
        for name in validated_data.keys():
            if name not in self._nested_serializers_forward:
                continue
            if isinstance(validated_data[name], (dict, list)):
                serializer = self.fields[name]
                serializer.read_only = True
                disabled_serializers.append(serializer)

        return disabled_serializers

    def _pop_reverse_data(self, validated_data):
        return {
            name: validated_data.pop(name)
            for name in list(validated_data.keys())
            if name in self._nested_serializers_reverse
        }

    def _reactivate_serializers(self, disabled_serializers):
        for serializer in disabled_serializers:
            serializer.read_only = False

    def _handle_reverse_nested(self, instance, reverse_data):
        for name, value in reverse_data.items():
            if value is None:
                continue
            model_field = self.Meta.model._meta.get_field(name)
            if isinstance(model_field, (models.OneToOneRel, models.ManyToOneRel)):
                if not isinstance(value, list):
                    value[model_field.field.name] = instance
                else:
                    for entry in value:
                        entry[model_field.field.name] = instance
        for name, value in reverse_data.items():
            nested_serializer = self.fields[name]

            model_field = self.Meta.model._meta.get_field(nested_serializer.source)

            if isinstance(model_field, models.OneToOneRel):
                previous_instance = getattr(instance, nested_serializer.source, None)
                pk_name = get_pk_name(nested_serializer)
                next_instance = getattr(value, pk_name, None)
                if previous_instance is not None and previous_instance != next_instance:
                    if model_field.field.null:
                        setattr(previous_instance, model_field.field.name, None)
                        previous_instance.save()
                    else:
                        previous_instance.delete()
            elif isinstance(model_field, models.ManyToOneRel):
                previous_instances = getattr(instance, nested_serializer.source).all()
                pk_name = get_pk_name(nested_serializer)
                next_instances = [
                    entry[pk_name]
                    for entry in value
                    if entry.get(pk_name, None) is not None
                ]

                for entry in previous_instances:
                    if entry not in next_instances:
                        if model_field.field.null:
                            setattr(entry, model_field.field.name, None)
                        else:
                            entry.delete()
            elif isinstance(model_field, models.ManyToManyRel):
                previous_instances = getattr(instance, nested_serializer.source).all()
                pk_name = get_pk_name(nested_serializer)
                next_instances = [
                    entry[pk_name]
                    for entry in value
                    if entry.get(pk_name, None) is not None
                ]

                for entry in previous_instances:
                    if entry not in next_instances:
                        entry.delete()

        result = self._update_or_create_nested(
            reverse_data, self._nested_serializers_reverse
        )
        for name, value in result.items():
            nested_serializer = self.fields[name]
            model_field = self.Meta.model._meta.get_field(nested_serializer.source)

            if model_field.multiple:
                getattr(instance, nested_serializer.source).set(value)

    def _update_or_create_nested(self, validated_data, relations):
        result = {}
        for name, value in validated_data.items():
            if name not in relations or value is None:
                continue

            if not isinstance(value, Sequence):
                result[name] = self._update_or_create_nested_entry(name, value)
            else:
                result[name] = [
                    self._update_or_create_nested_entry(name, entry) for entry in value
                ]
        return result

    def _update_or_create_nested_entry(self, name, value):
        serializer = self._nested_serializers[name]
        if isinstance(serializer, ListSerializer):
            serializer = serializer.child
        pk_name = get_pk_name(serializer)
        instance = value.pop(pk_name, None)
        if instance is None:
            return serializer.create(value)
        else:
            return serializer.update(instance, value)

    @cached_property
    def _nested_serializers_forward(self):
        field_info = model_meta.get_field_info(self.Meta.model)
        return {
            name: field
            for name, field in self._nested_serializers.items()
            if name in field_info.forward_relations
        }

    @cached_property
    def _nested_serializers_reverse(self):
        field_info = model_meta.get_field_info(self.Meta.model)
        return {
            name: field
            for name, field in self._nested_serializers.items()
            if name in field_info.reverse_relations
        }

    @cached_property
    def _nested_serializers(self):
        include = getattr(self.Meta, INCLUDE_FIELD, None)
        exclude = getattr(self.Meta, EXCLUDE_FIELD, None)

        assert (
            include is None or include == ALL_FIELDS or isinstance(include, Sequence)
        ), (
            f"The '{INCLUDE_FIELD}' option must be a sequence or '{ALL_FIELDS}'. Got '{include}'."
        )
        assert (
            exclude is None or exclude == ALL_FIELDS or isinstance(exclude, Sequence)
        ), (
            f"The '{exclude}' option must be a sequence or '{ALL_FIELDS}'. Got '{exclude}'."
        )
        assert not (include is not None and exclude is not None), (
            f"Cannot set both '{INCLUDE_FIELD}' and '{EXCLUDE_FIELD}' options on serializer '{type(self).__name__}'."
        )

        serializers = {
            field.source: field
            for field in self.fields.values()
            if isinstance(field, ModelSerializer)
            or isinstance(field, ListSerializer)
            and isinstance(field.child, ModelSerializer)
        }

        # None, None
        if include is None and exclude is None:
            return serializers
        # ALL, (None, List)
        elif include == ALL_FIELDS:
            return serializers
        # (None, List), ALL
        elif exclude == ALL_FIELDS:
            return {}
        # List, None
        elif include is not None:
            return {
                name: field
                for name, field in serializers.items()
                if field.field_name in include
            }
        # None, List
        elif exclude is not None:
            return {
                name: field
                for name, field in serializers.items()
                if field.field_name not in exclude
            }
        return {}


def get_pk_name(serializer):
    if isinstance(serializer, ListSerializer):
        serializer = serializer.child

    return serializer.Meta.model._meta.pk.attname
