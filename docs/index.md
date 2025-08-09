# DRF Nested Serializer

Adds support for writable nested serializers to the Django REST framework.

Find out more with the [Getting Started](https://gniludio.github.io/drf-nested-model-serializer/getting_started) guide.

## Features

- All relationship types
    - Including through model
- Drop-in replacement
- Create and update support
- Flexible field in- and exclusion
- Model Observer for [djangochannelsrestframework](https://github.com/NilCoalescing/djangochannelsrestframework)

## Example

```python hl_lines="10"
from rest_framework.serializers import ModelSerializer
from drf_nested_model_serializer.serializer import NestedModelSerializer
from .models import MyChildModel, MyParentModel

class MyChildSerializer(ModelSerializer):
    class Meta:
        model = MyChildModel
        fields = ("id", "")

class MyParentSerializer(NestedModelSerializer):
    nested = MyChildSerializer()

    class Meta:
        model = MyParentModel
        fields = ("id", "nested")

```

```python
data = {
    "child": {
        "name": "John Doe"
    }
}
serializer = MyParentSerializer(data=data)
if serializer.is_valid():
    instance = serializer.save()
```

```python
print(MyParentSerializer(instance=instance).data)
{
    "id": 1,
    "child": {
        "id": 1,
        "name": "John Doe"
    }
}
```
