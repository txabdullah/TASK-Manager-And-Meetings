from celery import shared_task


@shared_task
def process_meeting_notes(meeting_notes_id):
    """Extract tasks from meeting notes and create Task + TaskAssignment records."""
    from .models import MeetingNotes
    from .services import extract_tasks_from_notes, create_tasks_from_extraction

    try:
        notes = MeetingNotes.objects.select_related("meeting", "meeting__team", "meeting__created_by").get(
            pk=meeting_notes_id
        )
    except MeetingNotes.DoesNotExist:
        return {"error": "MeetingNotes not found", "id": meeting_notes_id}

    extracted = extract_tasks_from_notes(notes)
    if not extracted:
        return {"meeting_notes_id": meeting_notes_id, "tasks_created": 0}

    created = create_tasks_from_extraction(notes, extracted)
    for task in created:
        for assignment in task.assignments.select_related("assignee"):
            try:
                from apps.notifications.services import create_task_assigned_notification
                create_task_assigned_notification(assignment.assignee, task)
            except Exception:
                pass
    return {"meeting_notes_id": meeting_notes_id, "tasks_created": len(created)}
