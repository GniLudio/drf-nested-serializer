from functools import partial

from .nested_model_observer import NestedModelObserver


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
