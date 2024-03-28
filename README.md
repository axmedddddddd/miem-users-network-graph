# MIEM Users Network Graph

MIEM Users Network Graph is a web service designed to visualize the interconnected network of members, leaders, and projects within the MIEM (Moscow Institute of Electronics and Mathematics) faculty. This service is composed of two microservices: GraphMaker for backend processing and GraphExplorer for frontend presentation.

## GraphMaker (Backend)

GraphMaker is a Python-based microservice that interfaces with the MIEM cabinet public API to fetch project data, processes it accordingly, and stores it in a ClickHouse database. Additionally, it converts this data into graph structures and caches the output as JSON for efficient retrieval.

### Prerequisites
- Python 3.10
- Access to the MIEM cabinet public API
- ClickHouse database

## GraphExplorer (Frontend)

GraphExplorer is a TypeScript-based microservice that fetches the graph data from the cached JSON and renders it in a web interface, allowing for interactive exploration of the network.

### Prerequisites
- TypeScript and npm
- React

## Quickstart

To install and start the MIEM Users Network Graph, navigate to the root directory of the cloned repository and run:
```docker-compose up```

## Features
- Real-time visualization of the MIEM faculty projects
- Interactive graph elements
- Data caching for improved performance
- Integrated professional interests of teachers