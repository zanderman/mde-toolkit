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


def speed_grader_url(canvas: Canvas, course_id: int, assignment_id: int, student_id: int):
    return f"{canvas._Canvas__requester.original_url}/courses/{course_id}/gradebook/speed_grader?assignment_id={assignment_id}&student_id={student_id}"


from xml.etree import ElementTree
from xml.sax import saxutils
import networkx as nx
def parse_drive_architecture_xml(tree: ElementTree) -> nx.MultiGraph:
    root = tree.getroot()

    nodes = []
    edges = []
    for element in root.findall('./diagram/mxGraphModel/root/mxCell'):

        # Node.
        if 'value' in element.attrib:
            element.attrib['value'] = saxutils.unescape(element.attrib['value'])
            nodes.append((element.attrib['id'], {'attributes': element.attrib}))

        # Arrows for edges.
        elif 'source' in element.attrib or 'target' in element.attrib:
            edges.append((element.attrib['source'], element.attrib['target']))

    # Build network graph.
    graph = nx.MultiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    return graph


import os
def build_directory_structure_from_graph(graph: nx.MultiGraph, source: str) -> dict:

    def get_node_value(node: str) -> str:
        return graph.nodes[node]['attributes']['value']

    paths = {}
    paths[source] = get_node_value(source)
    iter = nx.bfs_successors(graph, source)
    for node,successors in iter:
        for s in successors:
            paths[s] = os.path.join(paths[node], get_node_value(s))

    return paths


def build_directories(graph: nx.MultiGraph, paths: dict, root: str):
    for key, path in paths.items():
        newpath = os.path.join(root, path)
        if not os.path.exists(newpath):
            os.makedirs(newpath)
            logger.info(newpath)


if __name__ == '__main__':
    tree = ElementTree.parse("/Volumes/GoogleDrive/Shared drives/ECE MDE /Drive Architecture/mde_drive_architecture.drawio.xml")
    graph = parse_drive_architecture_xml(tree)
    source = 'jZPj-5loQ12BBoLkCjAN-1' # Root node for hierarchy.
    paths = build_directory_structure_from_graph(graph, source)
    root = "/Volumes/GoogleDrive/Shared drives/ECE MDE /Drive Architecture/architecture_test"
    build_directories(graph, paths, root)
