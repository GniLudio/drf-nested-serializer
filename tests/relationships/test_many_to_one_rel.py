from django import test
from django.db import models
from rest_framework.serializers import ModelSerializer

from drf_nested_serializer.serializer import NestedSerializer
from tests.relationships.test_relationship import RelationshipTest


class ManyToOneRelParentModel(models.Model):
    pass


class ManyToOneRelNestedModel(models.Model):
    name = models.CharField()
    parent = models.ForeignKey(
        ManyToOneRelParentModel,
        related_name="nested",
        on_delete=models.CASCADE,
        null=True,
    )


class ManyToOneRelNestedSerializer(ModelSerializer):
    class Meta:
        model = ManyToOneRelNestedModel
        fields = ("id", "name")


class ManyToOneRelParentSerializer(NestedSerializer):
    nested = ManyToOneRelNestedSerializer(many=True, required=False, allow_empty=True)

    class Meta:
        model = ManyToOneRelParentModel
        fields = ("id", "nested")


class ManyToOneRelTest(RelationshipTest, test.TestCase):
    def test_create_omit_no(self):
        data = {}
        expected_valid = True
        expected = {"id": 1, "nested": []}

        serializer = ManyToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_none_no(self):
        pass

    def test_create_empty_no(self):
        data = {"nested": []}
        expected_valid = True
        expected = {"id": 1, "nested": []}

        serializer = ManyToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_withoutpk_no(self):
        data = {
            "nested": [
                {"name": "Max Mustermann"},
                {"name": "Erika Musterfrau"},
            ]
        }
        expected_valid = True
        expected = {
            "id": 1,
            "nested": [
                {"id": 1, "name": "Max Mustermann"},
                {"id": 2, "name": "Erika Musterfrau"},
            ],
        }

        serializer = ManyToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_withnonepk_no(self):
        data = {
            "nested": [
                {"id": None, "name": "Max Mustermann"},
                {"id": None, "name": "Erika Musterfrau"},
            ]
        }
        expected_valid = True
        expected = {
            "id": 1,
            "nested": [
                {"id": 1, "name": "Max Mustermann"},
                {"id": 2, "name": "Erika Musterfrau"},
            ],
        }

        serializer = ManyToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_onlypk_no(self):
        data = {
            "nested": [
                {"id": 3},
                {"id": 5},
            ]
        }
        expected_valid = True
        expected = {
            "id": 1,
            "nested": [
                {"id": 3, "name": "Max Mustermann"},
                {"id": 5, "name": "Erika Musterfrau"},
            ],
        }

        ManyToOneRelNestedModel.objects.create(id=3, name="Max Mustermann")
        ManyToOneRelNestedModel.objects.create(id=5, name="Erika Musterfrau")

        serializer = ManyToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_withpk_no(self):
        data = {
            "nested": [
                {"id": 3, "name": "Max Mustermann"},
                {"id": 5, "name": "Erika Musterfrau"},
            ]
        }
        expected_valid = True
        expected = {
            "id": 1,
            "nested": [
                {"id": 3, "name": "Max Mustermann"},
                {"id": 5, "name": "Erika Musterfrau"},
            ],
        }

        ManyToOneRelNestedModel.objects.create(id=3, name="Paul Beispielmann")
        ManyToOneRelNestedModel.objects.create(id=5, name="Erna Beispielfrau")

        serializer = ManyToOneRelParentSerializer(data=data)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_create_multiple_no(self):
        data_list = [
            {},  # Omit
            {"nested": []},
            {
                "nested": [
                    {"name": "Max Mustermann"},  # Without pk
                    {"id": None, "name": "Erika Musterfrau"},  # With `None` pk
                    {"id": 3},  # Only pk
                    {"id": 5, "name": "Paul Beispielmann"},  # With pk
                ]
            },
            {
                "nested": [
                    {"name": "Max Mustermann"},  # Without pk
                    {"id": None, "name": "Erika Musterfrau"},  # With `None` pk
                    {"id": 3},  # Only pk
                    {"id": 5, "name": "Erna Beispielfrau"},  # With pk
                ]
            },
        ]
        expected_valid = True
        expected_list = [
            {"id": 1, "nested": []},
            {"id": 2, "nested": []},
            {
                "id": 3,
                "nested": [
                    {"id": 6, "name": "Max Mustermann"},
                    {"id": 7, "name": "Erika Musterfrau"},
                ],
            },
            {
                "id": 4,
                "nested": [
                    {"id": 3, "name": "John Doe"},
                    {"id": 5, "name": "Erna Beispielfrau"},
                    {"id": 8, "name": "Max Mustermann"},
                    {"id": 9, "name": "Erika Musterfrau"},
                ],
            },
        ]

        ManyToOneRelNestedModel.objects.create(id=3, name="John Doe")
        ManyToOneRelNestedModel.objects.create(id=5, name="Jane Doe")

        instance_list = []
        for i in range(len(data_list)):
            data = data_list[i]

            serializer = ManyToOneRelParentSerializer(data=data)
            assert serializer.is_valid() == expected_valid, serializer.errors
            instance_list.append(serializer.save())

        for i in range(max(len(data_list), len(expected_list))):
            instance = instance_list[i]
            expected = expected_list[i]

            result = ManyToOneRelParentSerializer(instance=instance).data
            assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_omit_no(self):
        data = {}
        expected_valid = True
        expected = {"id": 3, "nested": []}

        parent = ManyToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_omit_yes(self):
        data = {}
        expected_valid = True
        expected = {"id": 5, "nested": [{"id": 3, "name": "Max Mustermann"}]}

        parent = ManyToOneRelParentModel.objects.create(id=5)
        ManyToOneRelNestedModel.objects.create(
            id=3, name="Max Mustermann", parent=parent
        )
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_none_no(self):
        pass

    def test_update_none_yes(self):
        pass

    def test_update_empty_no(self):
        data = {"nested": []}
        expected_valid = True
        expected = {"id": 3, "nested": []}

        parent = ManyToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_empty_yes(self):
        data = {"nested": []}
        expected_valid = True
        expected = {"id": 3, "nested": []}

        parent = ManyToOneRelParentModel.objects.create(id=3)
        nested = ManyToOneRelNestedModel.objects.create(
            id=5, name="Max Mustermann", parent=parent
        )
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withoutpk_no(self):
        data = {"nested": [{"name": "Max Mustermann"}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 1, "name": "Max Mustermann"}]}

        parent = ManyToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withoutpk_yes(self):
        data = {"nested": [{"name": "Max Mustermann"}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 6, "name": "Max Mustermann"}]}

        parent = ManyToOneRelParentModel.objects.create(id=3)
        ManyToOneRelNestedModel.objects.create(
            id=5, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withnonepk_no(self):
        data = {"nested": [{"id": None, "name": "Max Mustermann"}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 1, "name": "Max Mustermann"}]}

        parent = ManyToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withnonepk_yes(self):
        data = {"nested": [{"id": None, "name": "Max Mustermann"}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 6, "name": "Max Mustermann"}]}

        parent = ManyToOneRelParentModel.objects.create(id=3)
        ManyToOneRelNestedModel.objects.create(
            id=5, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlypk_no(self):
        data = {"nested": [{"id": 5}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 5, "name": "Max Mustermann"}]}

        ManyToOneRelNestedModel.objects.create(id=5, name="Max Mustermann")
        parent = ManyToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlypk_yes(self):
        data = {"nested": [{"id": 5}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 5, "name": "Max Mustermann"}]}

        ManyToOneRelNestedModel.objects.create(id=5, name="Max Mustermann")
        parent = ManyToOneRelParentModel.objects.create(id=3)
        ManyToOneRelNestedModel.objects.create(
            id=7, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_onlysamepk_yes(self):
        data = {"nested": [{"id": 5}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 5, "name": "Max Mustermann"}]}

        parent = ManyToOneRelParentModel.objects.create(id=3)
        ManyToOneRelNestedModel.objects.create(
            id=5, name="Max Mustermann", parent=parent
        )
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withpk_no(self):
        data = {"nested": [{"id": 5, "name": "Max Mustermann"}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 5, "name": "Max Mustermann"}]}

        ManyToOneRelNestedModel.objects.create(id=5, name="Erika Musterfrau")
        parent = ManyToOneRelParentModel.objects.create(id=3)
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withpk_yes(self):
        data = {"nested": [{"id": 5, "name": "Max Mustermann"}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 5, "name": "Max Mustermann"}]}

        ManyToOneRelNestedModel.objects.create(id=5, name="Erika Musterfrau")
        parent = ManyToOneRelParentModel.objects.create(id=3)
        ManyToOneRelNestedModel.objects.create(
            id=7, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_withsamepk_yes(self):
        data = {"nested": [{"id": 5, "name": "Max Mustermann"}]}
        expected_valid = True
        expected = {"id": 3, "nested": [{"id": 5, "name": "Max Mustermann"}]}

        parent = ManyToOneRelParentModel.objects.create(id=3)
        ManyToOneRelNestedModel.objects.create(
            id=5, name="Erika Musterfrau", parent=parent
        )
        instance = parent

        serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
        assert serializer.is_valid() == expected_valid, serializer.errors
        instance = serializer.save()
        result = ManyToOneRelParentSerializer(instance=instance).data
        assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_multiple_no(self):
        data_list = [
            {},  # Omit
            {"nested": []},
            {
                "nested": [
                    {"name": "Max Mustermann"},  # Without pk
                    {"id": None, "name": "Erika Musterfrau"},  # With `None` pk
                    {"id": 3},  # Only pk
                    {"id": 5, "name": "Paul Beispielmann"},  # With pk
                ]
            },
            {
                "nested": [
                    {"name": "Max Mustermann"},  # Without pk
                    {"id": None, "name": "Erika Musterfrau"},  # With `None` pk
                    {"id": 3},  # Only pk
                    {"id": 5, "name": "Erna Beispielfrau"},  # With pk
                ]
            },
        ]
        expected_valid = True
        expected_list = [
            {"id": 3, "nested": []},
            {"id": 5, "nested": []},
            {
                "id": 7,
                "nested": [
                    {"id": 6, "name": "Max Mustermann"},
                    {"id": 7, "name": "Erika Musterfrau"},
                ],
            },
            {
                "id": 9,
                "nested": [
                    {"id": 3, "name": "John Doe"},
                    {"id": 5, "name": "Erna Beispielfrau"},
                    {"id": 8, "name": "Max Mustermann"},
                    {"id": 9, "name": "Erika Musterfrau"},
                ],
            },
        ]

        ManyToOneRelNestedModel.objects.create(id=3, name="John Doe")
        ManyToOneRelNestedModel.objects.create(id=5, name="Jane Doe")
        parent_list = [
            ManyToOneRelParentModel.objects.create(id=3),
            ManyToOneRelParentModel.objects.create(id=5),
            ManyToOneRelParentModel.objects.create(id=7),
            ManyToOneRelParentModel.objects.create(id=9),
        ]

        instance_list = []
        for i in range(len(data_list)):
            data = data_list[i]
            instance = parent_list[i]

            serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
            assert serializer.is_valid() == expected_valid, serializer.errors
            instance_list.append(serializer.save())

        for i in range(max(len(data_list), len(expected_list))):
            instance = instance_list[i]
            expected = expected_list[i]

            result = ManyToOneRelParentSerializer(instance=instance).data
            assert result == expected, f"\nResult:   {result}\nExpected: {expected}"

    def test_update_multiple_yes(self):
        data_list = [
            {},  # Omit
            {"nested": []},
            {
                "nested": [
                    {"name": "Max Mustermann"},  # Without pk
                    {"id": None, "name": "Erika Musterfrau"},  # With `None` pk
                    {"id": 3},  # Only pk
                    {"id": 5, "name": "Paul Beispielmann"},  # With pk
                ]
            },
            {
                "nested": [
                    {"name": "Max Mustermann"},  # Without pk
                    {"id": None, "name": "Erika Musterfrau"},  # With `None` pk
                    {"id": 3},  # Only pk
                    {"id": 5, "name": "Erna Beispielfrau"},  # With pk
                ]
            },
        ]
        expected_valid = True
        expected_list = [
            {"id": 3, "nested": [{"id": 6, "name": "Foo 1"}]},
            {"id": 5, "nested": []},
            {
                "id": 7,
                "nested": [
                    {"id": 10, "name": "Max Mustermann"},
                    {"id": 11, "name": "Erika Musterfrau"},
                ],
            },
            {
                "id": 9,
                "nested": [
                    {"id": 3, "name": "John Doe"},
                    {"id": 5, "name": "Erna Beispielfrau"},
                    {"id": 12, "name": "Max Mustermann"},
                    {"id": 13, "name": "Erika Musterfrau"},
                ],
            },
        ]

        ManyToOneRelNestedModel.objects.create(id=3, name="John Doe")
        ManyToOneRelNestedModel.objects.create(id=5, name="Jane Doe")
        parent_list = [
            ManyToOneRelParentModel.objects.create(id=3),
            ManyToOneRelParentModel.objects.create(id=5),
            ManyToOneRelParentModel.objects.create(id=7),
            ManyToOneRelParentModel.objects.create(id=9),
        ]
        parent_list[0].nested.set(
            [ManyToOneRelNestedModel.objects.create(name="Foo 1")]
        )
        parent_list[1].nested.set(
            [ManyToOneRelNestedModel.objects.create(name="Foo 2")]
        )
        parent_list[2].nested.set(
            [ManyToOneRelNestedModel.objects.create(name="Foo 3")]
        )
        parent_list[3].nested.set(
            [ManyToOneRelNestedModel.objects.create(name="Foo 4")]
        )

        instance_list = []
        for i in range(len(data_list)):
            data = data_list[i]
            instance = parent_list[i]

            serializer = ManyToOneRelParentSerializer(data=data, instance=instance)
            assert serializer.is_valid() == expected_valid, serializer.errors
            instance_list.append(serializer.save())

        for i in range(max(len(data_list), len(expected_list))):
            instance = instance_list[i]
            expected = expected_list[i]

            result = ManyToOneRelParentSerializer(instance=instance).data
            assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
