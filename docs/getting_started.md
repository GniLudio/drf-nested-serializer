# DRF Getting Started

## Usage

```python
from django.db import models
from rest_framework.serializers import ModelSerializer
from drf_nested_serializer.serializer import NestedSerializer
from .models import MyNestedModel, MyParentModel

class MyNestedSerializer(ModelSerializer):
    class Meta:
        model = MyNestedModel
        fields = ("id", "name")

class MyParentSerializer(NestedSerializer):
    nested = MyNestedSerializer(required=False, allow_null=True)

    class Meta:
        model = MyParentModel
        fields = ("id", "nested")
```

### Saving Data

=== "Omit"

    TODO

=== "`None`"

    TODO

=== "Without pk"

    TODO

=== "With `None` pk"

    TODO

=== "Only pk"

    TODO

=== "With pk"

    TODO

### Inclusion and Exclusion

TODO

### On Remove

TODO

### Remarks

-   Always adds a `PrimaryKeyRelatedField` to nested serializers.
-   When passing the primary key, all fields are set to `required=False` for validation.
