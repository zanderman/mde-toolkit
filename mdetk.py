"""MDE Toolkit Library.

This module contains functions that aid MDE course operation.
"""
from canvasapi import Canvas
from canvasapi.user import User
from canvasapi.group import Group
import logging
from typing import Dict, Tuple

logger = logging.getLogger()


def get_users_by_group(canvas: Canvas, course_id: int) -> Tuple[Dict[int,User],Dict[int,Group],Dict[int,int]]:
    """Retrieve users correlated by group.

    Args:
        canvas (Canvas): Authenticated Canvas API object
        course_id (int): ID of course to query

    Returns:
        Tuple[Dict[int,User],Dict[int,Group],Dict[int,int]]: Tuple of 3 dictionaries:
            1. Dictionary of students
            2. Dictionary of groups
            3. Dictionary of student-id-to-group-id
    """

    # Get the course.
    course = canvas.get_course(course_id)

    # Load all groups.
    groups = [group for group in course.get_groups()]
    logger.debug("Loaded %d groups", len(groups))

    # There could be duplicate groups, with different `group_category_id` fields.
    # So, filter the group list to a single `group_category_id` field.
    group_category_ids = sorted(list(set([group.group_category_id for group in groups])))
    groups = {group.id:group for group in filter(lambda group: group.group_category_id == group_category_ids[0], groups)}
    logger.debug("Filtered to %d groups", len(groups))

    # Match groups to students.
    students = {}
    student_to_group = {}
    for _, g in groups.items():
        users = g.get_users()
        for u in users:
            students[u.id] = u
            student_to_group[u.id] = g.id

    return students, groups, student_to_group