"""MDE Canvas Helper Program.

Automates MDE tasks by interacting with Canvas directly.

This program requires there to be a Canvas API token in a `.env` file.
"""
from canvasapi import Canvas
from dataclasses import dataclass, asdict
from dotenv import dotenv_values

COURSE_NAME, COURSE_ID = "Fall 2021 ECE 4805", 136329


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
users = [user for user in course.get_users(enrollment_type=['student'])]
print(f'got users {len(users)}')
for user in users:
    print(f"name={user.name}, id={user.id}")

# courses = canvas.get_courses()
# for course in courses:
#     # Some courses may not be fully formed, need to handle those cases!
#     try:
#         print(course.name, course.id)
#     except:
#         pass