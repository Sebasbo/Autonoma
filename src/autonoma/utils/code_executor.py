"""CodeExecutor module for the Autonoma package."""

import tempfile
import os
import sys
import subprocess
import ast
from unittest.mock import MagicMock
from types import ModuleType
import pkgutil
from typing import List, Dict, Set
from autonoma.models import ExecutionResult


class CodeExecutor:
    """Executes code with mocking capabilities for external modules."""

    def __init__(self):
        """Initialize the CodeExecutor with stdlib modules."""
        self.mocked_modules: Dict[str, MagicMock] = {}
        self.stdlib_modules: Set[str] = set(m.name for m in pkgutil.iter_modules())
        self.stdlib_modules.update(sys.builtin_module_names)

    def analyze_imports(self, code: str) -> List[str]:
        """
        Analyze the code to find all import statements.

        Args:
            code: The code to analyze.

        Returns:
            A list of imported module names.
        """
        tree = ast.parse(code)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module.split(".")[0])
        return imports

    def is_external_module(self, module_name: str, codebase: Dict[str, str]) -> bool:
        """
        Check if a module is external (not in stdlib or codebase).

        Args:
            module_name: The name of the module to check.
            codebase: The current codebase.

        Returns:
            True if the module is external, False otherwise.
        """
        if module_name in self.stdlib_modules:
            return False
        if any(module_name in file_path for file_path in codebase.keys()):
            return False
        return True

    def create_mock_module(self, module_name: str) -> MagicMock:
        """
        Create a mock module.

        Args:
            module_name: The name of the module to mock.

        Returns:
            A MagicMock object representing the mocked module.
        """
        mock_module = MagicMock(spec=ModuleType(module_name))
        mock_module.__name__ = module_name
        mock_module.__file__ = f"/mock/{module_name}.py"
        mock_module.__path__ = [f"/mock/{module_name}"]
        mock_module.__loader__ = MagicMock()
        mock_module.__spec__ = MagicMock()
        return mock_module

    def mock_external_modules(self, code: str, codebase: Dict[str, str]) -> None:
        """
        Mock external modules found in the code.

        Args:
            code: The code to analyze for external modules.
            codebase: The current codebase.
        """
        imports = self.analyze_imports(code)
        for module_name in imports:
            if self.is_external_module(module_name, codebase):
                if module_name not in self.mocked_modules:
                    self.mocked_modules[module_name] = self.create_mock_module(module_name)

    def patch_modules(self) -> None:
        """Patch sys.modules with mocked modules."""
        for module_name, mock_module in self.mocked_modules.items():
            sys.modules[module_name] = mock_module

    def unpatch_modules(self) -> None:
        """Remove mocked modules from sys.modules."""
        for module_name in self.mocked_modules:
            if module_name in sys.modules:
                del sys.modules[module_name]

    def run(self, code: str, codebase: Dict[str, str]) -> ExecutionResult:
        """
        Run the given code in the context of the provided codebase.

        Args:
            code: The code to execute.
            codebase: The current codebase.

        Returns:
            An ExecutionResult object containing the execution results.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create the project structure
            for file_path, file_content in codebase.items():
                full_path = os.path.join(temp_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                with open(full_path, "w") as f:
                    f.write(file_content)

            # Create a __main__.py file with the code to execute
            main_file = os.path.join(temp_dir, "__main__.py")
            with open(main_file, "w") as f:
                f.write(code)

            # Mock external modules
            self.mock_external_modules(code, codebase)
            self.patch_modules()

            try:
                # Prepare the Python command
                python_command = [
                    sys.executable,
                    "-c",
                    f"import sys; sys.path.insert(0, '{temp_dir}'); import __main__",
                ]

                # Run the code
                result = subprocess.run(
                    python_command, capture_output=True, text=True, timeout=10, cwd=temp_dir
                )

                return ExecutionResult(
                    success=result.returncode == 0,
                    output=result.stdout if result.returncode == 0 else result.stderr,
                    mocked_modules=list(self.mocked_modules.keys()),
                )
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    success=False,
                    output="Execution timed out",
                    mocked_modules=list(self.mocked_modules.keys()),
                )
            except Exception as e:
                return ExecutionResult(
                    success=False, output=str(e), mocked_modules=list(self.mocked_modules.keys())
                )
            finally:
                # Clean up
                self.unpatch_modules()
