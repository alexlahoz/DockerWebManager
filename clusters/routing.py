from django.urls import re_path
from . import consumers


websocket_urlpatterns = [
  re_path(r'^containers/console/(?P<cid>[^/]+)/$', consumers.CommandConsumer.as_asgi()),
]
