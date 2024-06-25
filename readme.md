# Autonoma

Autonoma is a Python package for creating and managing autonomous AI agents. It provides tools for generating project plans, creating specialized agents including a ToolCrafterAgent, and executing complex software development tasks.

## Features

- Dynamic project plan generation using GPT-4
- Specialized AI agents for various development roles
- ToolCrafterAgent for creating custom tools on-the-fly
- Docker support for easy deployment
- Poetry for dependency management

## Installation

1. Clone the repository:
    git clone https://github.com/yourusername/autonoma.git
2. Install dependencies using Poetry:
    cd autonoma
    poetry install
3. Set up your OpenAI API key:
    export OPENAI_API_KEY=your_api_key_here
## Usage

Here's a basic example of how to use Autonoma:

```python
from autonoma import ProjectManager

# Initialize the project manager
project_manager = ProjectManager(api_key="your_openai_api_key")

# Generate a project plan
project_request = "Create a web application for a bookstore with user authentication, product catalog, shopping cart, and payment integration."
project_plan = project_manager.generate_project_plan(project_request)

# Execute the project plan
project_manager.execute_project_plan(project_plan)