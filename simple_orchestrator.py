#!/usr/bin/env python3
"""Simple orchestrator that works with Claude Code directly."""

import sys
from pathlib import Path


class SimpleCustDevOrchestrator:
    """Simple orchestrator that prints prompts for Claude Code to execute."""

    def __init__(self, prompts_dir: str = "prompts", outputs_dir: str = "outputs"):
        self.prompts_dir = Path(prompts_dir)
        self.outputs_dir = Path(outputs_dir)
        self.current_step = 0
        self.project_path = None

    def create_project_directory(self, idea: str) -> Path:
        """Create project directory."""
        # Sanitize idea name
        project_name = idea.lower().replace(" ", "-")[:50]
        project_name = ''.join(c for c in project_name if c.isalnum() or c == '-')

        project_path = self.outputs_dir / project_name
        project_path.mkdir(parents=True, exist_ok=True)

        return project_path

    def read_prompt(self, prompt_file: str) -> str:
        """Read prompt template."""
        prompt_path = self.prompts_dir / prompt_file
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt not found: {prompt_path}")
        return prompt_path.read_text(encoding='utf-8')

    def read_file(self, filename: str) -> str:
        """Read file from project directory."""
        file_path = self.project_path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return file_path.read_text(encoding='utf-8')

    def get_step_info(self, step: int, idea: str = "") -> dict:
        """Get information for a specific step."""
        steps = {
            1: {
                "name": "Startup Structurer",
                "prompt_file": "1 startup mix.md",
                "output_file": "1-startup-mix.md",
                "description": "Структурирование стартап-идеи",
                "input_context": f"Стартап-идея: {idea}"
            },
            2: {
                "name": "Question Generator",
                "prompt_file": "2 questions.md",
                "output_file": "2-questions.md",
                "description": "Генерация вопросов для интервью",
                "input_context": "Используй описание аудитории из файла 1-startup-mix.md"
            },
            3: {
                "name": "Persona Creator",
                "prompt_file": "3 person.md",
                "output_file": "3-person-{:02d}.md",
                "description": "Создание персон (10 штук)",
                "input_context": "Используй описание аудитории из файла 1-startup-mix.md",
                "count": 10
            },
            4: {
                "name": "Interview Simulator",
                "prompt_file": "4 script.md",
                "output_file": "4-script-{:02d}.md",
                "description": "Симуляция интервью (10 штук)",
                "input_context": "Используй персоны из 3-person-*.md и вопросы из 2-questions.md",
                "count": 10
            },
            5: {
                "name": "Interview Analyzer",
                "prompt_file": "5 analyse.md",
                "output_file": "5-analyse.md",
                "description": "Анализ всех интервью",
                "input_context": "Проанализируй все интервью из файлов 4-script-*.md"
            },
            6: {
                "name": "Reels Scriptwriter",
                "prompt_file": "6 reels.md",
                "output_file": "6-reels.md",
                "description": "Создание сценариев для видео",
                "input_context": "Используй 1-startup-mix.md и 5-analyse.md"
            }
        }
        return steps.get(step, {})

    def print_step_instruction(self, step: int, idea: str = ""):
        """Print instruction for Claude Code to execute a step."""
        step_info = self.get_step_info(step, idea)

        print("\n" + "="*70)
        print(f"ШАГ {step}: {step_info['name']}")
        print(f"Описание: {step_info['description']}")
        print("="*70)

        # Read prompt
        try:
            prompt = self.read_prompt(step_info['prompt_file'])

            print(f"\nПромпт из файла: {step_info['prompt_file']}")
            print("-"*70)
            print(prompt)
            print("-"*70)

            # Add context
            if 'input_context' in step_info:
                print(f"\nКонтекст: {step_info['input_context']}")

            # Output instructions
            if 'count' in step_info:
                print(f"\nСоздай {step_info['count']} файлов:")
                for i in range(1, step_info['count'] + 1):
                    output_file = step_info['output_file'].format(i)
                    print(f"  - {self.project_path}/{output_file}")
            else:
                print(f"\nСоздай файл: {self.project_path}/{step_info['output_file']}")

            print("="*70 + "\n")

        except FileNotFoundError as e:
            print(f"Ошибка: {e}")

    def run_interactive(self, idea: str):
        """Run orchestrator in interactive mode for Claude Code."""
        print("\n" + "="*70)
        print("CUSTDEV INTERVIEWER - Interactive Mode")
        print("="*70)
        print(f"Проект: {idea}")
        print("="*70)

        # Create project directory
        self.project_path = self.create_project_directory(idea)
        print(f"\nДиректория проекта: {self.project_path}")

        # Print all steps
        print("\n" + "="*70)
        print("ПЛАН ВЫПОЛНЕНИЯ:")
        print("="*70)
        for i in range(1, 7):
            step_info = self.get_step_info(i)
            print(f"{i}. {step_info['name']} - {step_info['description']}")
        print("="*70)

        # Print first step instruction
        print("\n\nСЕЙЧАС ВЫПОЛНЯЕМ:\n")
        self.print_step_instruction(1, idea)

        return self.project_path


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python simple_orchestrator.py \"Your startup idea\"")
        sys.exit(1)

    idea = sys.argv[1]

    orchestrator = SimpleCustDevOrchestrator()
    project_path = orchestrator.run_interactive(idea)

    print(f"\n\n{'='*70}")
    print("ИНСТРУКЦИИ ДЛЯ CLAUDE CODE:")
    print("="*70)
    print("""
После выполнения каждого шага, скажи мне "готово", и я дам тебе следующий шаг.

Для каждого шага:
1. Прочитай промпт выше
2. Прочитай контекстные файлы (если указаны)
3. Создай выходной файл в указанной директории
4. Скажи "готово"

Начинай с Шага 1!
""")
    print("="*70)


if __name__ == "__main__":
    main()
