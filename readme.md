# Autonoma: Autonomous Code Modification and Analysis

Autonoma is a powerful Python package that leverages AI to autonomously modify and analyze codebases. It uses advanced language models to understand code, generate modifications, and ensure quality through automated testing.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage Guide](#usage-guide)
  - [Core Concepts](#core-concepts)
  - [Configuring Agents](#configuring-agents)
  - [Custom Tasks](#custom-tasks)
  - [Best Practices](#best-practices)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

## Features

- 🧠 AI-powered code analysis and modification
- 🔄 Autonomous iterative improvement of code changes
- 🧪 Automated testing of modifications
- 📊 Detailed reporting of changes and thought processes
- 🛠 Extensible architecture for custom agents and tasks
## Agentic Framework Implementation

Autonoma is built upon the principles of the Agentic Framework, implementing a sophisticated multi-agent system for advanced software development. 🧠🔧 

Key aspects of our implementation include:

- **Multi-Agent System**: Autonoma integrates Large Language Models (LLMs) with specialized agents, including a PlannerAgent, CoderAgent, and Tester, operating asynchronously within an event-driven architecture.

- **Collaborative Workflow**: These agents work in concert to generate, refactor, and rigorously test code through an iterative process of continuous improvement. 🔄

- **Advanced Technologies**: 
  • Pydantic for robust data validation and serialization
  • Asynchronous operations for efficient multi-agent coordination
  • Advanced prompt engineering techniques for optimal LLM interaction
  • Static code analysis and abstract syntax tree (AST) manipulation for deep code insights

The result is a self-improving system that significantly enhances the reliability and quality of AI-generated code, while simultaneously addressing the complexity of modern software development. 🚀🔬

## Installation

Install Autonoma using pip:

```bash
pip install autonoma
```

## Quick Start

Here's a simple example of how to use Autonoma to modify a Python function:

```python
from autonoma import AutonomaAgent
from autonoma.models import CodeFile
from your_llm_package import YourLLMInterface  # Replace with your actual LLM interface

# Initialize your language model interface
llm_interface = YourLLMInterface()

# Initialize the Autonoma agent
agent = AutonomaAgent(llm_interface)

# Prepare your codebase
codebase = [
    CodeFile(
        path="example.py",
        content="""
def greet(name):
    print(f"Hello, {name}!")
"""
    )
]

# Define your query
query = "Modify the greet function to return the greeting instead of printing it."

# Process the query
result = agent.process_query(query, codebase)

# Print the modified code
print("Modified code:")
print(result.project_result.modified_files["example.py"])

# Print the thought process
print("\nThought process:")
for thought in result.project_result.thought_process:
    print(f"- {thought}")
```

## Usage Guide

### Core Concepts

Autonoma is built around several key concepts:

1. **AutonomaAgent**: The main class that orchestrates the entire process of code modification and analysis.
2. **PlannerAgent**: Responsible for creating a plan of tasks based on the user's query.
3. **CoderAgent**: Generates and modifies code based on tasks and test results.
4. **Tester**: Runs tests on the modified code to ensure correctness.
5. **Models**: Pydantic models that represent various entities like Project, Task, CodeFile, etc.

### Configuring Agents

You can customize the behavior of Autonoma by configuring its agents:

```python
from autonoma import AutonomaAgent, PlannerAgent, CoderAgent, Tester

custom_planner = PlannerAgent(llm_interface, max_tasks=5)
custom_coder = CoderAgent(llm_interface, style_guide="pep8")
custom_tester = Tester(llm_interface, test_framework="pytest")

agent = AutonomaAgent(
    llm_interface,
    planner_agent=custom_planner,
    coder_agent=custom_coder,
    tester=custom_tester
)
```

### Custom Tasks

You can define custom tasks for Autonoma to perform:

```python
from autonoma.models import Task, TaskType

custom_task = Task(
    id="task_001",
    description="Implement error handling for network operations",
    task_type=TaskType.CODE_IMPLEMENTATION,
    file_paths=["network_utils.py"],
    estimated_complexity="Medium"
)

# Add the custom task to your project
project.agents[0].tasks.append(custom_task)
```

### Best Practices

1. Provide clear and specific queries for best results.
2. Start with small, well-defined tasks before moving to larger refactoring projects.
3. Review and test the modified code thoroughly before integrating it into your project.
4. Use version control to track changes made by Autonoma.
5. Customize the agents to match your project's coding standards and practices.

## API Reference

### AutonomaAgent

The main class for interacting with Autonoma.

```python
class AutonomaAgent:
    def __init__(self, llm_interface: Any, planner_agent: Optional[PlannerAgent] = None,
                 coder_agent: Optional[CoderAgent] = None, tester: Optional[Tester] = None):
        ...

    def process_query(self, query: str, code_base: List[CodeFile]) -> FinalResult:
        ...

    def execute_project(self, project: Project, code_base: List[CodeFile]) -> ProjectResult:
        ...

    def execute_task(self, task: Task, agent: Agent, codebase: List[CodeFile]) -> TaskResult:
        ...
```

### PlannerAgent

Responsible for creating a plan of tasks based on the user's query.

```python
class PlannerAgent:
    def __init__(self, llm_interface: Any, max_tasks: int = 10):
        ...

    def create_query_plan(self, plan_request: PlanRequest) -> Project:
        ...
```

### CoderAgent

Generates and modifies code based on tasks and test results.

```python
class CoderAgent:
    def __init__(self, llm_interface: Any, style_guide: str = "pep8"):
        ...

    def generate_code(self, task: Task, agent: Agent) -> GeneratedCode:
        ...

    def modify_code_based_on_test(self, code: GeneratedCode, test: str, test_result: str, task: Task) -> GeneratedCode:
        ...
```

### Tester

Runs tests on the modified code to ensure correctness.

```python
class Tester:
    def __init__(self, llm_interface: Any, test_framework: str = "unittest"):
        ...

    def run_tests(self, modified_code: GeneratedCode, codebase: List[CodeFile]) -> Tuple[List[TestResult], List[TestResult]]:
        ...

    def generate_test_code(self, code: GeneratedCode) -> TestCodeResponse:
        ...
```

For a complete list of models and their attributes, please refer to the `models` module in the source code.

## Examples

### Basic Usage

See the [Quick Start](#quick-start) section for a basic usage example.

### Custom LLM Integration

Here's an example of how to integrate a custom language model:

```python
from autonoma import AutonomaAgent
from your_custom_llm import CustomLLM

class CustomLLMInterface:
    def __init__(self):
        self.model = CustomLLM()

    def generate(self, prompt: str) -> str:
        return self.model.generate_text(prompt)

llm_interface = CustomLLMInterface()
agent = AutonomaAgent(llm_interface)

# Use the agent as normal
```

### Large-Scale Refactoring

```python
from autonoma import AutonomaAgent
from autonoma.models import CodeFile
import os

def load_codebase(directory):
    codebase = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                with open(path, 'r') as f:
                    content = f.read()
                codebase.append(CodeFile(path=path, content=content))
    return codebase

# Load your entire project
codebase = load_codebase('./your_project_directory')

# Initialize the agent
agent = AutonomaAgent(your_llm_interface)

# Define a large-scale refactoring task
query = """
Refactor the entire project to use type hints consistently.
Also, update all functions to use docstrings in the Google style.
"""

# Process the query
result = agent.process_query(query, codebase)

# Review and apply the changes
for file_path, new_content in result.project_result.modified_files.items():
    print(f"Modifying {file_path}")
    with open(file_path, 'w') as f:
        f.write(new_content)

print("Refactoring complete!")
```

## Contributing

We welcome contributions to Autonoma! Here's how you can help:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bug fix.
3. Write your code and tests.
4. Ensure all tests pass by running `pytest`.
5. Submit a pull request with a clear description of your changes.

Please read our [Contributing Guide](CONTRIBUTING.md) for more details on our code of conduct and development process.

## License

Autonoma is released under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Support

If you encounter any issues or have questions, please [file an issue](https://github.com/yourusername/autonoma/issues) on our GitHub repository. For general discussions or questions, join our [community forum](https://forum.autonoma.dev).

---

We hope you find Autonoma useful in your projects! Happy coding!
