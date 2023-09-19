from django.urls import re_path, path
from . import consumers


websocket_urlpatterns = [
  re_path(r'^containers/console/(?P<cid>[^/]+)/$', consumers.CommandConsumer.as_asgi()),
  # path('ws/containers', consumers.DetailConsumer.as_asgi())
  re_path(r'^containers/detail/(?P<cid>[^/]+)/$', consumers.DetailConsumer.as_asgi()),
]
