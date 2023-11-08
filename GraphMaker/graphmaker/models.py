from datetime import date, datetime
from pydantic import BaseModel
from enum import Enum
from dataclasses import dataclass


@dataclass
class UserNode:
    id: str
    full_name: str
    short_name: str
    role: str
    in_project_duration: int


@dataclass
class ProjectNode:
    id: str
    name: str
    type: str


@dataclass
class Edge:
    source: UserNode
    target: ProjectNode
    width: int
    group: str

class GroupBy(Enum):
    id = "id"
    projectIndustryLabel = "projectIndustryLabel"


class MemberStatus(BaseModel):
    id: int
    name: str
    code: str
    projectOwner: int
    utpStatus: int


class TeamMember(BaseModel):
    fullName: str
    name: str
    userId: int
    id: int
    email: list[str]
    first_name: str
    last_name: str
    middle_name: str
    chatLink: str
    dep: str
    group: str
    startDate: datetime | None
    endDate: datetime | None
    gitId: int
    isTeacher: bool
    ownerPrivilege: int
    pic: str
    role: str
    telnum: str
    trelloId: str
    utpStatus: int
    vacancy_id: int
    initiator: bool
    external: bool
    status: list[MemberStatus]


class LeaderStatus(BaseModel):
    id: int
    code: str
    name: str


class TeamLeader(BaseModel):
    id: int
    fio: str
    name: str
    first_name: str
    last_name: str
    middle_name: str
    email: list[str]
    telnum: str | None
    ownerPrivilege: int
    status: list[LeaderStatus]
    role: str


class Project(BaseModel):
    id: int
    owner: bool
    status: str
    statusDesc: str
    nameRus: str
    head: str
    directionHead: str
    type: str
    typeDesc: str
    typeId: int
    statusId: int
    dateCreated: str
    vacancies: int
    team: list[str]
    vacancyData: list
    number: str
    desc: str | None
    hoursCount: int
    facultyId: str | None
    thumbnail: str | None
    detailed_team: list[TeamMember]
    projectIndustryLabel: str
    leaders: list[TeamLeader]


class Node(BaseModel):
    key: str
    label: str
    tag: str
    URL: str
    cluster: str
    x: float
    y: float
    score: float

    class Config:
        frozen = True


class Cluster(BaseModel):
    key: str
    color: str
    clusterLabel: str

    class Config:
        frozen = True


class Tag(BaseModel):
    key: str
    image: str

class Response(BaseModel):
    nodes: list[Node]
    edges: list[list]
    clusters: list[Cluster]
    tags: list[Tag]
