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
import numpy as np
import sys

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
@click.option('--delimiter','-d', type=str, default='|', help="Output record delimiter")
@click.option('--sort-by', '-s', type=click.Choice(['user_name', 'user_id'], case_sensitive=False), default='user_id', show_default=True)
@pass_canvas
def students(canvas, course_id, delimiter, sort_by):

    # Get course object and all student objects.
    course = canvas.get_course(course_id)
    students = [student for student in course.get_users(enrollment_type=['student'])]

    # Set sorting key.
    if sort_by == 'user_name':
        key = lambda student: student.sortable_name
    elif sort_by == 'user_id':
        key = lambda student: student.id
    else:
        raise ValueError('sorting key not defined')

    # Print students in sorted order.
    header_items = ['user id', 'user name']
    header = delimiter.join(header_items)
    print(header)
    for student in sorted(students, key=key):
        print(f"{student.id}{delimiter}{student.sortable_name}")


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


@cli.command()
@click.option('--course-id', '-c', required=True, type=int)
@click.option('--bins', '-b', required=True, type=str, help='number of even-sized bins, or space-delimited list of bin size percentages')
@click.option('--delimiter','-d', type=str, default='|', help="Output record delimiter")
@click.option('--report', '-r', is_flag=True)
@click.option('--write-files','-w', is_flag=True)
@click.option('--sort-by', '-s', type=click.Choice(['none', 'user_name', 'group_name', 'user_id', 'group_id'], case_sensitive=False), default='none', show_default=True)
@pass_canvas
def bin_students(canvas, course_id, bins, delimiter, report, write_files, sort_by):

    # Bins provided as integer number of bins.
    try:
        bins = int(bins)
        percentages = [1./bins for _ in range(bins)]

    # Bins provided as space-delimited list of size percentages.
    except:
        percentages = [float(s) for s in bins.split(' ')]
        bins = len(percentages)

    # Verify that percentages sum to 100.
    if sum(percentages) != 1.0:
        raise ValueError('Percentages must sum to 1')

    # Get linked users to groups.
    users, groups, user_to_group = mdetk.get_users_by_group(canvas, course_id)

    # Organize list of user IDs, in various sorting orders.
    if sort_by == 'user_name':
        uids = np.array(sorted(users.keys(), key=lambda uid: users[uid].sortable_name))
    elif sort_by == 'group_name':
        uids = np.array(sorted(users.keys(), key=lambda uid: groups[user_to_group[uid]].name))
    if sort_by == 'user_id':
        uids = np.array(sorted(users.keys(), key=lambda uid: uid))
    elif sort_by == 'group_id':
        uids = np.array(sorted(users.keys(), key=lambda uid: user_to_group[uid]))
    else:
        uids = np.array(list(users.keys()))

    # Split the users into bins.
    nuids = len(uids)
    sections = [int(np.ceil(nuids*(p+(sum(percentages[:i]) if i > 0 else 0)))) for i, p in enumerate(percentages[:-1])]
    binned = np.split(uids, sections)

    # Summarize the binning results if necessary.
    if report:
        print(f"Summary", file=sys.stderr)
        print(f"=======", file=sys.stderr)
        print(f"Groups: {len(groups)}", file=sys.stderr)
        print(f"Users: {nuids}", file=sys.stderr)
        print(f"Bins: {bins}", file=sys.stderr)
        for i, bin in enumerate(binned):
            print(f"Bin {i+1}: {len(bin)} users ({percentages[i]*100}%)", file=sys.stderr)

    header_items = ['bin id', 'item number', 'user id', 'user name', 'group id', 'group name']
    header = delimiter.join(header_items)
    if write_files:
        # Output the binning results.
        for i, bin in enumerate(binned):
            with open(f"bin_{i+1}.csv", 'w') as f:
                f.write(f"{header}")
                for j, uid in enumerate(bin):
                    records = [
                        i+1,
                        j+1,
                        uid,
                        users[uid].sortable_name,
                        groups[user_to_group[uid]].id,
                        groups[user_to_group[uid]].name,
                    ]
                    f.write(f"\n{delimiter.join(str(r) for r in records)}")
    else:
        # Output the binning results.
        print(f"{header}")
        for i, bin in enumerate(binned):
            for j, uid in enumerate(bin):
                records = [
                    i+1,
                    j+1,
                    uid,
                    users[uid].sortable_name,
                    groups[user_to_group[uid]].id,
                    groups[user_to_group[uid]].name,
                ]
                print(f"{delimiter.join(str(r) for r in records)}")


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