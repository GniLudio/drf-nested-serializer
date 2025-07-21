# Testing

All tests have the following structure:

<!--
Success: &#x2705;
Failure: &#x274C;
With: &check;
Without: -
-->

```python
def test_foo(self):
    data = {...}
    expected_valid = True # or False
    expected = {...} # or omitted

    # setup (without serializer)
    ...

    # testing
    serializer = MyParentSerializer(data=data, ...)
    # validate data
    assert serializer.is_valid() == expected_valid, serializer.errors
    # derserialization
    instance = serializer.save()
    # serialization
    result = MyParentSerializer(instance=instance).data
    # validate result
    assert result == expected, f"\nResult:   {result}\nExpected: {expected}"
```

## Relationships

<!--
Action: Create / Update
    Nested Data: Omit / None / Empty / Without pk / With `None` pk / Only pk / Only same pk / With pk / With same pk / Multiple
        Previous Nested: Without / With
-->

| Action |  Nested Data   | Previous Nested | One to One | One to One Rel | Foreign Key | Many to One Rel | Many to Many | Many to Many Rel | Through |
|-------:|:--------------:|:---------------:|:----------:|:--------------:|:-----------:|:---------------:|:------------:|:----------------:|:-------:|
| Create |      Omit      |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Create |     `None`     |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Create |     Empty      |       \-        |     -      |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Create |   Without pk   |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Create | With `None` pk |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Create |    Only pk     |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Create |    With pk     |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Create |    Multiple    |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |      Omit      |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |      Omit      |     &check;     |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |     `None`     |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |     `None`     |     &check;     |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |     Empty      |       \-        |     -      |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |     Empty      |     &check;     |     -      |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |   Without pk   |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |   Without pk   |     &check;     |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update | With `None` pk |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update | With `None` pk |     &check;     |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |    Only pk     |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |    Only pk     |     &check;     |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |  Only same pk  |     &check;     |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |    With pk     |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |    With pk     |     &check;     |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |  With same pk  |     &check;     |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |    Multiple    |       \-        |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |
| Update |    Multiple    |     &check;     |  &#x2705;  |    &#x2705;    |  &#x2705;   |    &#x2705;     |   &#x2705;   |     &#x2705;     |         |


## Other
* Non-nullable: &#x2705;
* Nesting: &#x2705;
* Source: TODO
* Write-only: TODO
* Delete-action: TODO
* Partial update: TODO
* Allow empty: TODO
* Allow null: TODO
* Doc examples: TODO
* Validation: TODO