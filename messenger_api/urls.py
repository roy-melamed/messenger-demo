from django.urls import path
from .views import (
    MessagesApiView,
    RegisterView,
    MessagesByUserView,
    InboxView,
    OutboxView,
)

urlpatterns = [
    path('messages/', MessagesApiView.as_view()),
    path('messages/by-user/<id>/', MessagesByUserView.as_view()),
    path('messages/inbox/', InboxView.as_view()),
    path('messages/outbox/', OutboxView.as_view()),
    path('register/', RegisterView.as_view(), name='auth_register'),
]
