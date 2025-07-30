# DRF Getting Started

## Usage

A serializer just needs to inherit from `NestedModelSerializer` to allow writable nested serializers:

=== "One to One"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedModelSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedModelSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedModelSerializer): # (1)
        nested = MyNestedModelSerializer()

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```
    
    1. Inherit `NestedModelSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        pass

    class MyParentModel(models.Model):
        nested = models.OneToOneField(MyNestedModel, on_delete=models.CASCADE)
    ```

=== "One to One Rel"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedModelSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedModelSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedModelSerializer): # (1)
        nested = MyNestedModelSerializer()

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedModelSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        parent = models.OneToOneField("MyParentModel", on_delete=models.CASCADE, related_name="nested")

    class MyParentModel(models.Model):
        pass
    ```

=== "Foreign Key"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedModelSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedModelSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedModelSerializer): # (1)
        nested = MyNestedModelSerializer()

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedModelSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        pass

    class MyParentModel(models.Model):
        nested = models.ForeignKey(MyNestedModel, on_delete=models.CASCADE)
    ```

=== "Many to One Rel"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedModelSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedModelSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedModelSerializer): # (1)
        nested = MyNestedModelSerializer(many=True)

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedModelSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        parent = models.ForeignKey("MyParentModel", on_delete=models.CASCADE, related_name="nested")

    class MyParentModel(models.Model):
        pass
    ```


=== "Many to Many"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedModelSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedModelSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedModelSerializer): # (1)
        nested = MyNestedModelSerializer(many=True)

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedModelSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        pass

    class MyParentModel(models.Model):
        nested = models.ManyToManyField(MyNestedModel)
    ```

=== "Many to Many Rel"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedModelSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyNestedModel, MyParentModel

    class MyNestedModelSerializer(ModelSerializer):
        class Meta:
            model = MyNestedModel
            fields = ("id", )

    class MyParentSerializer(NestedModelSerializer): # (1)
        nested = MyNestedModelSerializer(many=True)

        class Meta:
            model = MyParentModel
            fields = ("id", "nested")
    ```

    1. Inherit `NestedModelSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

    ```python
    from django.db import models

    class MyNestedModel(models.Model):
        parent = models.ManyToManyField(MyNestedModel, related_name="nested")

    class MyParentModel(models.Model):
        pass
    ```

=== "Through"

    ```python hl_lines="10"
    from drf_nested_serializer.serializer import NestedModelSerializer
    from rest_framework.serializers import ModelSerializer
    from .models import MyThroughModel, MyParentModel

    class MyThroughSerializer(ModelSerializer):
        class Meta:
            model = MyThroughModel
            fields = ("id", "nested")

    class MyParentSerializer(NestedModelSerializer): # (1)
        through = MyThroughSerializer(many=True)

        class Meta:
            model = MyParentModel
            fields = ("id", "through")
    ```

    1. Inherit from `NestedModelSerializer` to allow writable nested serializers (instead of `ModelSerializer`)

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


## Data

=== "Do nothing"
    
    ```python
    data = {

    }
    ```
    ```python
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "Set to `None`"

    ```python
    data = {
        "nested": None
    }
    ```
    ```python
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "Create new nested"

    ```python
    data = {
        "nested": { "id": None, "name": "John Doe"}
    }
    ```
    ```python
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "Set to existing"

    ```python
    data = {
        "nested": { "id": 3 }
    }
    ```
    ```python
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

=== "Set and update"

    ```json
    data = {
        "nested": { "id": 3, "name": "John Doe" }
    }
    ```
    ```python
    serializer = MyParentSerializer(data=data)
    if serializer.is_valid():
        instance = serializer.save()
    ```

## Inclusion and Exclusion

If not all nested serializers should be handled, you can explicitly include or exclude fields:

=== "Include all (default)"

    ```python
    class MyParentSerializer(NestedModelSerializer):
        ...
        class Meta:
            ...
            nested_include = "__all__" # or omitted
    ```

=== "Include specific"

    ```python
    class MyParentSerializer(NestedModelSerializer):
        ...
        class Meta:
            ...
            nested_include = ("field_1", "field_2", ...)
    ```

=== "Exclude all"

    ```python
    class MyParentSerializer(NestedModelSerializer):
        ...
        class Meta:
            ...
            nested_exclude = "__all__"
    ```

=== "Exclude specific"

    ```python
    class MyParentSerializer(NestedModelSerializer):
        ...
        class Meta:
            ...
            nested_exclude = ("field_1", "field_2", ...)
    ```
