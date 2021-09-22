"""MDE Canvas Helper Program.

Automates MDE tasks by interacting with Canvas directly.

This program requires there to be a Canvas API token in a `.env` file.
"""
from canvasapi import Canvas
from dataclasses import dataclass, asdict
from dotenv import dotenv_values

# COURSE_NAME, COURSE_ID = "Fall 2021 ECE 4805", 136329
# COURSE_NAME, COURSE_ID = "ECE 4806 MDE Fall 2021", 136333
COURSE_NAME, COURSE_ID = "ECE 4806 - MDE Spring 2021", 125412


@dataclass
class Config:
    CANVAS_API_URL: str = None
    CANVAS_API_TOKEN: str = None


# Default configuration.
default_config = Config(
    CANVAS_API_URL="https://canvas.vt.edu",
)

# Take environment variables from `.env` file.
ENV_FILE = ".env"
config = Config(
    **{
        **asdict(default_config),
        **dotenv_values(ENV_FILE),
    }
)

# Ensure that an API token was specified.
if config.CANVAS_API_TOKEN is None:
    raise ValueError('A Canvas API token is required')

# Initialize a new Canvas object
canvas = Canvas(config.CANVAS_API_URL, config.CANVAS_API_TOKEN)

# Get the desired course.
course = canvas.get_course(COURSE_ID)
print(course.name, course.id)

## Get all students in the course. 
# The `PaginatedList` type lazily loads elements.
# Must use list comprehension to force it to load everything.
# users = [user for user in course.get_users(enrollment_type=['student'])]
# print(f'got {len(users)} users')


# # Get all assignments for the course.
# assignments = [a for a in course.get_assignments()]
# for a in assignments:
#     print(a)

# # Get specific assignment.
# ASSIGNMENT_NAME, ASSIGNMENT_ID = "MDE EXPO submit final Presentation and Poster", 1278344
ASSIGNMENT_NAME, ASSIGNMENT_ID = "MDE EXPO submit final Presentation and Poster", 1119551
assignment = course.get_assignment(ASSIGNMENT_ID)
print(assignment.submissions_download_url)

import urllib.request
import tqdm

class TqdmUpTo(tqdm.tqdm):
    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""
    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        return self.update(b * bsize - self.n)  # also sets self.n = b * bsize

# with TqdmUpTo(unit='B', unit_scale=True, unit_divisor=1024, miniters=1, desc=assignment.submissions_download_url.split('/')[-1]) as t:  # all optional kwargs
#     urllib.request.urlretrieve(assignment.submissions_download_url, 'submissions.zip', reporthook=t.update_to)

urllib.request.urlretrieve(assignment.submissions_download_url, 'submissions.zip')

# # Get all submissions for an assignment.
# submissions = [s for s in assignment.get_submissions()]
# # print(submissions[0].url)
# for s in submissions:
#     print(s.attachments)
#     break





# courses = canvas.get_courses()
# for course in courses:
#     # Some courses may not be fully formed, need to handle those cases!
#     try:
#         print(course.name, course.id)
#     except:
#         pass