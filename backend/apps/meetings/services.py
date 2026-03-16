import re
from django.contrib.auth import get_user_model

User = get_user_model()

# Regex patterns for simulated task extraction
# "Ali will prepare the budget." -> (Ali, prepare the budget)
# "Sara will contact the supplier." -> (Sara, contact the supplier)
# "Assign to John: Review the report" -> (John, Review the report)
PATTERNS = [
    re.compile(r"(\w+)\s+will\s+(.+)", re.IGNORECASE),
    re.compile(r"(\w+)\s+to\s+(.+)", re.IGNORECASE),
    re.compile(r"assign\s+to\s+(\w+):\s*(.+)", re.IGNORECASE),
]


def extract_tasks_from_notes(meeting_notes):
    """
    Extract tasks from meeting notes using regex patterns.
    Returns list of dicts: [{"assignee_name": str, "description": str}, ...]
    """
    content = meeting_notes.content
    tasks = []
    seen = set()

    for line in content.split("\n"):
        line = line.strip()
        if not line:
            continue
        for pattern in PATTERNS:
            match = pattern.search(line)
            if match:
                assignee_name = match.group(1).strip()
                description = match.group(2).strip()
                key = (assignee_name.lower(), description.lower())
                if key not in seen:
                    seen.add(key)
                    tasks.append({"assignee_name": assignee_name, "description": description})
                break

    return tasks


def resolve_assignee(assignee_name, team, fallback_user):
    """
    Try to map a name to a team member. Falls back to fallback_user if not found.
    """
    name_lower = assignee_name.lower()
    for member in team.members.select_related("user"):
        user = member.user
        if (
            user.first_name.lower() == name_lower
            or user.last_name.lower() == name_lower
            or user.username.lower() == name_lower
            or (user.email and name_lower in user.email.lower())
        ):
            return user
    return fallback_user


def create_tasks_from_extraction(meeting_notes, extracted_tasks):
    """
    Create Task and TaskAssignment records from extracted task data.
    """
    from apps.tasks.models import Task, TaskAssignment

    meeting = meeting_notes.meeting
    team = meeting.team
    fallback_user = meeting.created_by

    created = []
    for item in extracted_tasks:
        assignee = resolve_assignee(
            item["assignee_name"],
            team,
            fallback_user,
        )
        task = Task.objects.create(
            meeting=meeting,
            team=team,
            title=item["description"][:255],
            description=item["description"],
            status="todo",
            created_by=fallback_user,
        )
        TaskAssignment.objects.create(task=task, assignee=assignee)
        created.append(task)
    return created
