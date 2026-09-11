# VHS tape recording the Task Tracker demo.
# Install VHS (https://github.com/charmbracelet/vhs) and run:
#   vhs assets/demo.tape
# Requires vhs <= 0.11.0 -- v0.12.0 has a regression where the render step
# receives an already-cancelled context and silently produces no output
# (https://github.com/charmbracelet/vhs/compare/v0.11.0...v0.12.0).
Output assets/demo.gif

Set Shell "bash"
Set FontSize 16
Set Width 1200
Set Height 650
Set Theme "Dracula"
Set TypingSpeed 40ms

Type "mkdir -p /tmp/task-tracker-demo && cd /tmp/task-tracker-demo && rm -f tasks.json"
Enter
Sleep 500ms

Type "alias task-cli='uv run --project ~/www/task-tracker task-cli'"
Enter
Sleep 500ms

Type "task-cli add 'Buy groceries'"
Enter
Sleep 1s

Type "task-cli add 'Cook dinner'"
Enter
Sleep 1s

Type "task-cli update 1 'Buy groceries and cook dinner'"
Enter
Sleep 1s

Type "task-cli mark-in-progress 1"
Enter
Sleep 1s

Type "task-cli mark-done 2"
Enter
Sleep 1s

Type "task-cli list"
Enter
Sleep 2s

Type "task-cli list done"
Enter
Sleep 1500ms

Type "task-cli delete 2"
Enter
Sleep 1500ms
