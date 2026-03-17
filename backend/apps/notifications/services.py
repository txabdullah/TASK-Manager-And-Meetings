from django.contrib.contenttypes.models import ContentType

from .models import Notification


def create_task_assigned_notification(assignee, task):
    """Create notification when a task is assigned."""
    ct = ContentType.objects.get_for_model(task)
    Notification.objects.create(
        user=assignee,
        notification_type="task_assigned",
        content_type=ct,
        object_id=task.pk,
        read=False,
    )


def create_new_comment_notification(comment, task):
    """Create notifications for assignee and task creator when a new comment is added."""
    ct = ContentType.objects.get_for_model(task)
    recipients = set()
    for assignment in task.assignments.all():
        if assignment.assignee_id != comment.author_id:
            recipients.add(assignment.assignee)
    if task.created_by and task.created_by_id != comment.author_id:
        recipients.add(task.created_by)
    for user in recipients:
        Notification.objects.create(
            user=user,
            notification_type="new_comment",
            content_type=ct,
            object_id=task.pk,
            read=False,
        )


def create_deadline_approaching_notification(user, task):
    """Create notification when task deadline is approaching."""
    ct = ContentType.objects.get_for_model(task)
    Notification.objects.create(
        user=user,
        notification_type="deadline_approaching",
        content_type=ct,
        object_id=task.pk,
        read=False,
    )
