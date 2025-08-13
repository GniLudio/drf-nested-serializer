from functools import partial

from django.db import models
from django.db import transaction
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.utils.translation import gettext as _
from djangochannelsrestframework.observer.model_observer import Action
from djangochannelsrestframework.observer.model_observer import ModelObserver
from rest_framework.serializers import ListSerializer


def nested_model_observer(model, serializer_class, many_to_many=False, **kwargs):
    """
    Should be used as a method decorator eg: `@nested_model_observer(MyModel, MySerializer)`

    The serializer class has to be a `NestedModelSerializer`.
    """
    return partial(
        NestedModelObserver,
        model_cls=model,
        serializer_class=serializer_class,
        many_to_many=many_to_many,
        **kwargs,
    )


class NestedModelObserver(ModelObserver):
    """
    Observer that automatically detects nested children from the serializer_class of the consumer.
    """

    def __init__(
        self,
        func,
        model_cls,
        serializer_class,
        partition="*",
        many_to_many=False,
        **kwargs,
    ):
        # Track pending parent updates to avoid duplicates
        self._pending_parent_updates = set()

        if serializer_class is None:
            raise ValueError(
                _("serializer_class must be provided for NestedModelObserver")
            )

        super().__init__(
            func, model_cls, partition, serializer_class, many_to_many, **kwargs
        )

    def _connect(self):
        super()._connect()

        if not self._serializer_class:
            return

        serializer = self._serializer_class()

        for field in serializer._nested_serializers.values():
            nested_serializer = (
                field.child if isinstance(field, ListSerializer) else field
            )

            child_model = getattr(
                getattr(nested_serializer, "Meta", None), "model", None
            )

            if not child_model:
                continue

            fk_field = self._find_fk_field(child_model, self.model_cls)
            if not fk_field:
                continue

            post_save.connect(
                self._make_child_save_receiver(fk_field),
                sender=child_model,
                dispatch_uid=f"{id(self)!s}-{child_model.__name__}-nested-save",
            )
            post_delete.connect(
                self._make_child_delete_receiver(fk_field),
                sender=child_model,
                dispatch_uid=f"{id(self)!s}-{child_model.__name__}-nested-delete",
            )

    def _find_fk_field(self, child_model, parent_model):
        for f in child_model._meta.fields:
            if isinstance(f, models.ForeignKey) and f.related_model == parent_model:
                return f.name
        return None

    def _schedule_parent_update(self, parent):
        """Schedule a parent update, but avoid duplicates within the same transaction."""
        parent_key = (parent.__class__, parent.pk)

        if parent_key in self._pending_parent_updates:
            return

        self._pending_parent_updates.add(parent_key)

        def _send_update():
            try:
                self.database_event(parent, Action.UPDATE)
            finally:
                self._pending_parent_updates.discard(parent_key)

        transaction.on_commit(_send_update)

    def _make_child_save_receiver(self, fk_field):
        def _receiver(sender, instance, created, **kwargs):
            self._reciver_body(instance, fk_field)

        return _receiver

    def _make_child_delete_receiver(self, fk_field):
        def _receiver(sender, instance, **kwargs):
            self._reciver_body(instance, fk_field)

        return _receiver

    def _reciver_body(self, instance, fk_field):
        parent = getattr(instance, fk_field, None)
        if parent:
            self._schedule_parent_update(parent)
