# DRF Getting Started

## Usage

A serializer just needs to inherit from `NestedSerializer` to allow writable nested serializers:

=== "One to One"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedSerializer): # (1)
        nested = MyNestedSerializer()

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```
    
    1. Inherit `NestedSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        pass

    class MyParentModel(models.Model):
        nested = models.OneToOneField(MyNestedModel, on_delete=models.CASCADE)
    ```

=== "One to One Rel"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedSerializer): # (1)
        nested = MyNestedSerializer()

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        parent = models.OneToOneField("MyParentModel", on_delete=models.CASCADE, related_name="nested")

    class MyParentModel(models.Model):
        pass
    ```

=== "Foreign Key"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedSerializer): # (1)
        nested = MyNestedSerializer()

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        pass

    class MyParentModel(models.Model):
        nested = models.ForeignKey(MyNestedModel, on_delete=models.CASCADE)
    ```

=== "Many to One Rel"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedSerializer): # (1)
        nested = MyNestedSerializer(many=True)

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        parent = models.ForeignKey("MyParentModel", on_delete=models.CASCADE, related_name="nested")

    class MyParentModel(models.Model):
        pass
    ```


=== "Many to Many"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedSerializer): # (1)
        nested = MyNestedSerializer(many=True)

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        pass

    class MyParentModel(models.Model):
        nested = models.ManyToManyField(MyNestedModel)
    ```

=== "Many to Many Rel"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedSerializer): # (1)
        nested = MyNestedSerializer(many=True)

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        parent = models.ManyToManyField(MyNestedModel, related_name="nested")

    class MyParentModel(models.Model):
        pass
    ```

=== "Through"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyThroughModel, MyParentModel

    class MyThroughSerializer(ModelSerializer):
        class Meta:
            model = MyThroughModel
            fields = ("id", "nested")

    class MyParentSerializer(NestedSerializer): # (1)
        through = MyThroughSerializer(many=True)

        class Meta:
            model = MyParentModel
            fields = ("id", "through")
    ```

    1. Inherit from `NestedSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        pass

    class MyParentModel(models.Model):
        nested = models.ManyToManyField(MyNestedModel, through="MyThroughModel")

    class MyThroughModel(models.Model):
        nested = models.ForeignKey(MyNestedModel, on_delete=models.CASCADE)
        parent = models.ForeignKey(MyParentModel, on_delete=models.CASCADE, related_name="through")
    ```




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

    > Sets `nested` to `None`

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
        "nested": {
        
            "name": "John Doe",
        }
    }
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```
    

=== "With `None` pk"

    > Creates a new nested instance

    ```python
    data = {
        "nested": {
            "id": None,
            "name": "John Doe",
        }
    }
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "Only pk"

    > Sets `nested` to an existing nested instance 

    ```python
    data = {
        "nested": {
            "id": 3,

        }
    }
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "With pk"

    > Sets `nested` to an existing nested instance and updates it

    ```python
    data = {
        "nested": {
            "id": 3,
            "name": "John Doe",
        }
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

By default removed instances are deleted. You can override that behavior with the `nested_remove_action` meta option:

```python
class MyParentSerializer(NestedSerializer):
    class Meta:
        ...
        nested_remove_action = {
            "nested": "__delete__" # to delete the removed instance
            "nested": "__null__" # to set reverse `OneToOne`/`ForeignKey` relation to `NULL`
        }

```

