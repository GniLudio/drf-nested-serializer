# DCRF Nested Model Observer

You can use `nested_model_observer` in the same way as the original `model_observer` from [djangochannelsrestframework](https://github.com/NilCoalescing/djangochannelsrestframework).
The only difference is that you must also provide a serializer class, which should inherit from `NestedModelSerializer`, as an additional argument.

Example:

```py
from djangochannelsrestframework.consumers import GenericAsyncAPIConsumer
from djangochannelsrestframework.decorators import action
from drf_nested_model_serializer.djangochannelsrestframework.observer import nested_model_observer

from .serializers import UserSerializer, CommentSerializer  # `CommentSerializer` inherit from `NestedModelSerializer`
from .models import User, Comment

class MyConsumer(GenericAsyncAPIConsumer):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @nested_model_observer(Comment, CommentSerializer)
    async def comment_activity(self, message, observer=None, subscribing_request_ids=[], **kwargs):
        for request_id in subscribing_request_ids:
            await self.send_json({"message": message, "request_id": request_id})

    @comment_activity.serializer
    def comment_activity(self, instance: Comment, action, **kwargs):
        return CommentSerializer(instance).data

    @action()
    async def subscribe_to_comment_activity(self, request_id, **kwargs):
        await self.comment_activity.subscribe(request_id=request_id)
```