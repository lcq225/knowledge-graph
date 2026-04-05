# Ontology v2.0 - Knowledge Graph

> Entity Recognition, Relation Extraction, Graph Query and Visualization

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![PyPI](https://img.shields.io/badge/PyPI-v2.0.0-green.svg)](https://pypi.org/project/copaw-ontology/)

## Overview

Ontology v2.0 is an advanced knowledge graph system with entity recognition, relation extraction, graph query, and visualization capabilities.

### Core Features

| Feature | Description |
|---------|-------------|
| **Entity Recognition** | Automatic entity detection and classification |
| **Relation Extraction** | Extract relationships between entities |
| **Graph Query** | SPARQL-like query language for graph traversal |
| **Visualization** | Interactive graph visualization with multiple layouts |
| **Ontology Management** | Class hierarchy, property inheritance, relation inference |

### Architecture

```
Ontology v2.0
├── Contracts       # Skill contracts with YAML format
├── Core
│   ├── Bus        # Event-driven communication
│   ├── Validator  # Constraint validation
│   ├── Contract   # Skill contract management
│   └── Coordinator # Skill lifecycle management
├── Schema          # Data schema definitions
├── Scripts         # Utility scripts
└── Tests          # Unit tests
```

## Installation

```bash
pip install copaw-ontology
```

## Quick Start

### 1. Build Index

```bash
knowledge-graph build_index
```

### 2. Query Ontology

```bash
knowledge-graph ontology_cli --help
```

### 3. Visualize Graph

```bash
knowledge-graph visualize_graph --output graph.html
```

## Documentation

- [API Documentation](API.md)

## Requirements

- Python 3.8+
- SQLAlchemy
- NetworkX
- PyYAML

## License

MIT License

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## Links

- GitHub: https://github.com/lcq225/copaw-ontology
- PyPI: https://pypi.org/project/copaw-ontology/
- Issues: https://github.com/lcq225/copaw-ontology/issues