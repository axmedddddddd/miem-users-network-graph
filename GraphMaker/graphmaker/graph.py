from dataclasses import dataclass
from datetime import datetime
from math import floor
import igraph as ig
import networkx as nx
import json
import numpy as np
import ast
import os
import graph
import models
from typing import List, Tuple, Any, Dict
from footprint_dftools import clickhouse as ch

from config import BaseConfig
config = BaseConfig()

import logging
logging.basicConfig(filename='backend.log', level=logging.INFO)
logger = logging.getLogger()

palette = [
    "#001219",
    "#005f73",
    "#0a9396",
    "#94d2bd",
    "#e9d8a6",
    "#ee9b00",
    "#ca6702",
    "#bb3e03",
    "#ae2012",
    "#9b2226",
]


@dataclass
class GroupChoices:
    ID = "id"
    TYPE_DESCRIPTION = "typeDesc"
    INDUSTRY_LABEL = "projectIndustryLabel"


def get_data_from_db() -> Dict[str, Any]:
    """Fetching table from CH"""
    client = ch.ClickHouseConnection(host=config.ch_host, port=config.ch_port, username=config.ch_user, password=config.ch_pass)
    df = client.read_database("SELECT * FROM sandbox.ongoing_projects")
    dict_data = df.to_dict(orient='records')

    json_fields = ['team', 'vacancyData', 'detailed_team', 'leaders']
    
    for record in dict_data:
        for field in json_fields:
            if field in record and record[field]:
                try:
                    record[field] = json.loads(record[field].replace("'", "\""))
                except json.JSONDecodeError:
                    try:
                        record[field] = ast.literal_eval(record[field])
                    except (ValueError, SyntaxError) as e:
                        print(f"Error evaluating JSON for {field} in record {record.get('id', 'Unknown')}: {e}")

    return dict_data


def get_color(n: int, palette: List[str]) -> str:
    """Get color for node based on tis key"""
    palette_size = len(palette)

    if n >= palette_size:
        idx = n - (palette_size * floor(n / palette_size))
        color = palette[idx]
    else:
        color = palette[n]

    return color
    
def get_short_name(fullName):
    name_parts = fullName.split()

    if len(name_parts) >= 3:
        short_name = f"{name_parts[0]} {name_parts[1][0]}.{name_parts[2][0]}."
    elif len(name_parts) == 2:
        short_name = f"{name_parts[0]} {name_parts[1][0]}."
    else:
        short_name = name_parts[0]

    return short_name


def extract_edges(project_data: dict, group_by: GroupChoices) -> Tuple[Any, Any, Any]:
    """Construct all the nodes and edges"""
    team = project_data["detailed_team"]

    leaders = project_data["leaders"]

    team_nodes = []
    for member in team:
        full_name = member["fullName"]
        
        short_name = get_short_name(full_name)

        if full_name is None:
            continue

        user_id = f"user_{member['id']}"
        role = member["role"]

        try:
            join_date = datetime.strptime(member["startDate"], "%d.%m.%Y")
        except ValueError:
            continue
        except TypeError:
            continue

        now = datetime.now()

        duration = now - join_date
        node = models.UserNode(
            id=user_id,
            full_name=full_name,
            short_name=short_name,
            role=role,
            in_project_duration=duration.days,
        )
        team_nodes.append(node)

    leader_nodes = []
    for leader in leaders:

        if leader["middle_name"] and leader["first_name"]:
            short_name = f"{leader['last_name']} {leader['first_name'][0]}.{leader['middle_name'][0]}"
        elif leader["first_name"]:
            short_name = f"{leader['last_name']} {leader['first_name'][0]}."
        else:
            short_name = f"{leader['last_name']}"

        full_name = leader["name"] if "name" in leader else leader["fio"]
        ownerPrivilege = leader["ownerPrivilege"]
        if full_name is None or ownerPrivilege == 0:
            continue

        user_id = f"user_{leader['id']}"
        role = leader["role"]

        try:
            join_date = datetime.strptime(
                project_data["dateCreated"], "%d.%m.%Y %H:%M:%S"
            )
        except ValueError:
            continue

        now = datetime.now()

        duration = now - join_date
        node = models.UserNode(
            id=user_id,
            full_name=full_name,
            short_name=short_name,
            role=role,
            in_project_duration=duration.days,
        )
        leader_nodes.append(node)

    group = project_data[group_by]
    project_id = f"project_{project_data['id']}"

    project_node = models.ProjectNode(
        id=project_id, name=project_data["nameRus"], type=project_data["type"]
    )
    edges = []
    all_nodes = {}
    for node in team_nodes:
        edge = models.Edge(
            source=node,
            target=project_node,
            width=node.in_project_duration / 100,
            group=group,
        )
        edges.append(edge)
        all_nodes[node.id] = node

    for node in leader_nodes:
        edge = models.Edge(
            source=node,
            target=project_node,
            width=node.in_project_duration / 100,
            group=group,
        )
        edges.append(edge)
        all_nodes[node.id] = node

    return edges, all_nodes, project_node


def make_graph(group_by: str = GroupChoices.INDUSTRY_LABEL) -> nx.Graph:
    """Make raw graph"""
    data = get_data_from_db()

    g = nx.DiGraph()
    nodes = {}
    project_nodes = {}
    group_to_id = {}

    for project in data:
        project_edges, project_team, project_node = extract_edges(
            project, group_by=group_by
        )
        for edge in project_edges:
            if edge.group not in group_to_id:
                group_to_id[edge.group] = len(group_to_id)

            color = get_color(group_to_id[edge.group], palette)
            g.add_edge(
                str(edge.source.id),  # Convert to string
                str(edge.target.id),  # Convert to string
                width=edge.width,
                group=str(edge.group),  # Convert to string
                group_id=str(group_to_id[edge.group]),  # Convert to string
                color=color,
                label=edge.group,
            )

        nodes.update(project_team)
        project_nodes[project_node.id] = project_node

    for source, target, data in g.edges(data=True):
        source_node = nodes[source]
        target_node = project_nodes[target]

        g.nodes[source]["label"] = source_node.short_name
        g.nodes[source][
            "title"
        ] = f"{source_node.full_name}</br>{source_node.role}</br>{source_node.in_project_duration}"
        g.nodes[source]["color"] = data["color"]
        g.nodes[source]["shape"] = "disc"
        g.nodes[source]["size"] = min(max([g.degree(source) / 2, 2]), 10)

        g.nodes[target]["label"] = target_node.name
        g.nodes[target]["title"] = f"{target_node.name}</br>{target_node.type}"
        g.nodes[target]["color"] = data["color"]
        g.nodes[target]["shape"] = "square"
        g.nodes[target]["size"] = min(max([g.degree(target) / 2, 2]), 10)

    return g


def formatted_graph(group: graph.GroupChoices, save_json: bool = False) -> None:
    """Converting graph into proper view and caching as option"""
    g = graph.make_graph(group_by=group)
    g = nx.relabel.convert_node_labels_to_integers(g, label_attribute="node_id")

    h = ig.Graph.from_networkx(g)
    
    rng = np.random.default_rng(10)
    start_positions = rng.random((g.number_of_nodes(), 2))
    
    np.random.seed(10)
    layout = h.layout_fruchterman_reingold(weights="width", grid=False, niter=2000, seed=start_positions)

    tags = [
        models.Tag(key="Person", image="person.svg"),
        models.Tag(key="Tool", image="tool.svg"),
    ]

    edges = []

    exists_nodes = set()
    nodes = set()
    clusters = set()
    for source, target, data in g.edges(data=True):
        source_node = g.nodes[source]
        target_node = g.nodes[target]

        edges.append([source, target])

        x_source, y_source = layout[source]
        x_target, y_target = layout[target]

        source_score = min(max([g.degree(source) / 2, 2]), 10)
        target_score = min(max([g.degree(target) / 2, 2]), 10)

        if source not in exists_nodes:
            source_node = models.Node(
                key=str(source),
                label=source_node["label"],
                cluster=str(data["group_id"]),
                x=x_source,
                y=y_source,
                tag="Person",
                score=source_score,
                URL="",
            )
            nodes.add(source_node)
            exists_nodes.add(source)

        if target not in exists_nodes:
            target_node = models.Node(
                key=str(target),
                label=target_node["label"],
                cluster=str(data["group_id"]),
                x=x_target,
                y=y_target,
                tag="Tool",
                score=target_score,
                URL="",
            )
            nodes.add(target_node)
            exists_nodes.add(target)

        cluster = models.Cluster(
            key=str(data["group_id"]), color=data["color"], clusterLabel=data["group"]
        )
        clusters.add(cluster)
    
    response = models.Response(nodes=nodes, edges=edges, clusters=clusters, tags=tags)
    
    if save_json:
        path_to_cache = os.path.join("/code/public/data", f"miem_{group}_graph.json")
        
        with open(path_to_cache, "w", encoding="utf-8") as f:
            json.dump(response.dict(), f, ensure_ascii=False)
        
        logger.info(f"Successfully built graph by_{group}_{datetime.now()}")

    return


if __name__ == "__main__":
    formatted_graph(group=graph.GroupChoices.INDUSTRY_LABEL, save_json=True)
    formatted_graph(group=graph.GroupChoices.ID, save_json=True)
