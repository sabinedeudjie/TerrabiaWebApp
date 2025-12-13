"""
Messaging app models - Conversations and Messages
"""
from django.db import models
from accounts.models import User
from orders.models import Order


class MessageThread(models.Model):
    """
    Message thread model for conversations between users.
    Can be linked to an order for order-related discussions.
    """
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True, related_name='threads')
    participants = models.ManyToManyField(User, related_name='threads')
    subject = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        if self.order:
            return f"Thread for Order {self.order.code}"
        return f"Thread {self.id}"

    def get_other_participant(self, user):
        """Get the other participant in a two-person thread."""
        participants = self.participants.exclude(id=user.id)
        return participants.first() if participants.exists() else None


class Message(models.Model):
    """
    Message model for individual messages in a thread.
    """
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender.username} in Thread {self.thread.id}"

    def mark_as_read(self, user):
        """Mark message as read by a user."""
        if user != self.sender:
            self.is_read = True
            self.save()
