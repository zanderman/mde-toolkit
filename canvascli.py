"""MDE Canvas Helper Program.

Automates MDE tasks by interacting with Canvas directly.

This program requires there to be a Canvas API token in a `.env` file.
"""

# TODO: Retrieve user and group
# TODO: Combinations of users for each GTA

from canvasapi import Canvas
import click
from dataclasses import dataclass, asdict
from dotenv import dotenv_values
import logging
import mdetk

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# COURSE_NAME, COURSE_ID = "Fall 2021 ECE 4805", 136329
# COURSE_NAME, COURSE_ID = "ECE 4806 MDE Fall 2021", 136333
COURSE_NAME, COURSE_ID = "ECE 4806 - MDE Spring 2021", 125412


@dataclass
class Config:
    CANVAS_API_URL: str = None
    CANVAS_API_TOKEN: str = None


# Decorator for passing the `Canvas` object to commands.
pass_canvas = click.make_pass_decorator(Canvas, ensure=True)


@click.group()
@click.option('--canvas-token', envvar='CANVAS_API_TOKEN', default=None)
@click.option('--canvas-url', envvar='CANVAS_API_URL', default='https://canvas.vt.edu')
@click.option('--env', default='.env')
@click.pass_context
def cli(ctx, canvas_url, canvas_token, env):

    # Build configuration.
    config = Config(
        **{
            'CANVAS_API_URL': canvas_url,
            'CANVAS_API_TOKEN': canvas_token,
            **dotenv_values(env),
        }
    )

    # Ensure that an API token was specified.
    if config.CANVAS_API_TOKEN is None:
        raise ValueError('A Canvas API token is required')

    # Create `Canvas` object and store inside context.
    ctx.obj = Canvas(config.CANVAS_API_URL, config.CANVAS_API_TOKEN)


@cli.command()
@pass_canvas
def courses(canvas):
    courses = canvas.get_courses()
    for course in courses:
        if hasattr(course, 'name'):
            print(f"{course.id},{course.name}")


@cli.command()
@click.option('--course-id', '-c', required=True, type=int)
@pass_canvas
def groups(canvas, course_id):
    course = canvas.get_course(course_id)
    for group in course.get_groups():
        print(f"{group.id},{group.name}")


@cli.command()
@click.option('--course-id', '-c', required=True, type=int)
@pass_canvas
def students(canvas, course_id):
    course = canvas.get_course(course_id)
    for student in course.get_users(enrollment_type=['student']):
        print(f"{student.id},{student.sortable_name}")


@cli.command()
@click.option('--course-id', '-c', required=True, type=int)
@click.option('--assignment-id', '-a', required=True, type=int)
@pass_canvas
def assignment(canvas, course_id, assignment_id):
    course = canvas.get_course(course_id)
    assignment = course.get_assignment(assignment_id)
    print(assignment.submissions_download_url)


@cli.command()
@click.option('--course-id', '-c', required=True, type=int)
@pass_canvas
def users_groups(canvas, course_id):

    # Get linked users to groups.
    users, groups, user_to_group = mdetk.get_users_by_group(canvas, course_id)

    # List of student IDs in sorted order based on `sortable_name` field.
    sorted_users = sorted(list((sid,s) for sid, s in users.items()), key=lambda tup: tup[1].sortable_name)

    # Print all users and groups.
    for sid, s in sorted_users:
        print(sid, s.sortable_name, '-->', groups[user_to_group[sid]].id, groups[user_to_group[sid]].name)


if __name__ == '__main__':
    cli()


# # Get the desired course.
# course = canvas.get_course(COURSE_ID)
# print(course.name, course.id)

# ## Get all students in the course. 
# # The `PaginatedList` type lazily loads elements.
# # Must use list comprehension to force it to load everything.
# # users = [user for user in course.get_users(enrollment_type=['student'])]
# # print(f'got {len(users)} users')


# # # Get all assignments for the course.
# # assignments = [a for a in course.get_assignments()]
# # for a in assignments:
# #     print(a)

# # # Get specific assignment.
# # ASSIGNMENT_NAME, ASSIGNMENT_ID = "MDE EXPO submit final Presentation and Poster", 1278344
# ASSIGNMENT_NAME, ASSIGNMENT_ID = "MDE EXPO submit final Presentation and Poster", 1119551
# assignment = course.get_assignment(ASSIGNMENT_ID)
# print(assignment.submissions_download_url)

# import urllib.request
# import tqdm

# class TqdmUpTo(tqdm.tqdm):
#     """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""
#     def update_to(self, b=1, bsize=1, tsize=None):
#         """
#         b  : int, optional
#             Number of blocks transferred so far [default: 1].
#         bsize  : int, optional
#             Size of each block (in tqdm units) [default: 1].
#         tsize  : int, optional
#             Total size (in tqdm units). If [default: None] remains unchanged.
#         """
#         if tsize is not None:
#             self.total = tsize
#         return self.update(b * bsize - self.n)  # also sets self.n = b * bsize

# # with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=assignment.submissions_download_url.split('/')[-1]) as t:  # all optional kwargs
# #     urllib.request.urlretrieve(assignment.submissions_download_url, 'submissions.zip', reporthook=t.update_to)

# urllib.request.urlretrieve(assignment.submissions_download_url, 'submissions.zip')

# # # Get all submissions for an assignment.
# # submissions = [s for s in assignment.get_submissions()]
# # # print(submissions[0].url)
# # for s in submissions:
# #     print(s.attachments)
# #     break





# # courses = canvas.get_courses()
# # for course in courses:
# #     # Some courses may not be fully formed, need to handle those cases!
# #     try:
# #         print(course.name, course.id)
# #     except:
# #         pass