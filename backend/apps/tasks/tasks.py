from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def send_task_reminders():
    """
    Check tasks with deadlines in the next 24 hours and create notifications.
    Run via Celery Beat every hour.
    """
    from apps.tasks.models import Task
    from apps.notifications.services import create_deadline_approaching_notification

    now = timezone.now()
    window_end = now + timedelta(hours=24)
    tasks = Task.objects.filter(
        deadline__gte=now,
        deadline__lte=window_end,
        status__in=("todo", "in_progress"),
    ).prefetch_related("assignments__assignee")

    notified = 0
    for task in tasks:
        for assignment in task.assignments.all():
            create_deadline_approaching_notification(assignment.assignee, task)
            notified += 1
        if not task.assignments.exists() and task.created_by:
            create_deadline_approaching_notification(task.created_by, task)
            notified += 1

    return {"tasks_checked": tasks.count(), "notifications_created": notified}
