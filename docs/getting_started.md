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

===

### Saving Data

=== "Omit"
    
    > Does nothing to `nested`

    ```python
    data = {
    }
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "`None`"

    > Sets nested to `None`

    ```python
    data = {
        "nested": None
    }
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "Without pk"

    > Creates a new nested instance

    ```python
    data = {
        "nested": None
    }
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```
    

=== "With `None` pk"

    > Creates a new nested instance

    ```python
    data = {
        "nested": None
    }
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "Only pk"

    > Sets `nested` to an existing nested instance 

    ```python
    data = {
        "nested": None
    }
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "With pk"

    > Sets `nested` to an existing nested instance and updates it

    ```python
    data = {
        "nested": None
    }
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

### Inclusion and Exclusion

By default all nested serializers are automatically handled, but you can explicitly specify which fields should be handled:

=== "Include all"

    ```python
    class MyParentSerializer(NestedSerializer):
        class Meta:
            ...
            nested_include = "__all__" # or omitted
    ```

=== "Include specific"

    ```python
    class MyParentSerializer(NestedSerializer):
        class Meta:
            ...
            nested_include = ("field_1", "field_2", ...)
    ```

=== "Exclude all"

    ```python
    class MyParentSerializer(NestedSerializer):
        class Meta:
            ...
            nested_exclude = "__all__"
    ```

=== "Exclude specific"

    ```python
    class MyParentSerializer(NestedSerializer):
        class Meta:
            ...
            nested_exclude = ("field_1", "field_2", ...)
    ```


### Remove Behavior

By default, the following happens to the nested instance if you remove it:
* `ForeignKey` - Nothing
* `ManyToManyField` - Nothing
* `ManyToOneRel`
    * Related field set to `None` if nullable
    * Otherwise deleted
* `OneToOneRel`
    * Related field set to `None` if nullable
    * Otherwise deleted

### Remarks

-   Always adds a `PrimaryKeyRelatedField` to nested serializers.
-   When passing the primary key, all fields are set to `required=False` for validation.
