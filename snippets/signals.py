from django.db.models.signals import post_save
from django.dispatch import receiver
from snippets.models import Comment, Following, Notification

@receiver(post_save, sender=Comment)
def notify_comment(sender, instance, created, **kwargs):
    if created:
        snippet_owner = instance.snippet.owner
        if instance.owner != snippet_owner:
            Notification.objects.create(
                recipient=snippet_owner,
                actor=instance.owner,
                verb="has commented on your snippet",
                target=instance.snippet
            )

@receiver(post_save, sender=Following)
def notify_follow(sender, instance, created, **kwargs):
    if created:
        followed_user = instance.user_followed
        Notification.objects.create(
            recipient=followed_user,
            actor=instance.user_follower,
            verb="has started following you",
            target=instance.user_follower
        )