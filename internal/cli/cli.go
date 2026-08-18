// Package cli parses positional command-line arguments and dispatches
// them to an *app.App, formatting results (or errors) for the terminal.
package cli

import (
	"fmt"
	"os"
	"strconv"

	"github.com/carvalhocaio/task-tracker/internal/app"
	"github.com/carvalhocaio/task-tracker/internal/task"
)

// Run executes the command described by args (typically os.Args[1:])
// against a and returns a process exit code.
func Run(a *app.App, args []string) int {
	if len(args) < 1 {
		printUsage()
		return 1
	}

	command, rest := args[0], args[1:]

	var err error
	switch command {
	case "add":
		err = runAdd(a, rest)
	case "update":
		err = runUpdate(a, rest)
	case "delete":
		err = runDelete(a, rest)
	case "mark-in-progress":
		err = runMark(a, rest, task.StatusInProgress)
	case "mark-done":
		err = runMark(a, rest, task.StatusDone)
	case "list":
		err = runList(a, rest)
	case "help", "-h", "--help":
		printUsage()
		return 0
	default:
		fmt.Fprintf(os.Stderr, "Error: unknown command %q\n\n", command)
		printUsage()
		return 1
	}

	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		return 1
	}

	return 0
}

func runAdd(a *app.App, args []string) error {
	if len(args) < 1 {
		return fmt.Errorf("usage: task-cli add <description>")
	}

	t, err := a.Add(args[0])
	if err != nil {
		return err
	}

	fmt.Printf("Task added successfully (ID: %d)\n", t.ID)
	return nil
}

func runUpdate(a *app.App, args []string) error {
	if len(args) < 2 {
		return fmt.Errorf("usage: task-cli update <id> <description>")
	}

	id, err := parseID(args[0])
	if err != nil {
		return err
	}

	if err := a.Update(id, args[1]); err != nil {
		return err
	}

	fmt.Printf("Task %d updated successfully\n", id)
	return nil
}

func runDelete(a *app.App, args []string) error {
	if len(args) < 1 {
		return fmt.Errorf("usage: task-cli delete <id>")
	}

	id, err := parseID(args[0])
	if err != nil {
		return err
	}

	if err := a.Delete(id); err != nil {
		return err
	}

	fmt.Printf("Task %d deleted successfully\n", id)
	return nil
}

func runMark(a *app.App, args []string, status task.Status) error {
	if len(args) < 1 {
		return fmt.Errorf("usage: task-cli mark-%s <id>", status)
	}

	id, err := parseID(args[0])
	if err != nil {
		return err
	}

	if err := a.SetStatus(id, status); err != nil {
		return err
	}

	fmt.Printf("Task %d marked as %s\n", id, status)
	return nil
}

func runList(a *app.App, args []string) error {
	var filter task.Status

	if len(args) > 0 {
		switch args[0] {
		case "done":
			filter = task.StatusDone
		case "todo":
			filter = task.StatusTodo
		case "in-progress":
			filter = task.StatusInProgress
		default:
			return fmt.Errorf("unknown filter %q (use: done, todo, in-progress)", args[0])
		}
	}

	tasks, err := a.List(filter)
	if err != nil {
		return err
	}

	if len(tasks) == 0 {
		fmt.Println("No tasks found.")
		return nil
	}

	for _, t := range tasks {
		fmt.Printf("[%d] %-12s %s (updated: %s)\n",
			t.ID, t.Status, t.Description, t.UpdatedAt.Format("2006-01-02 15:04"))
	}

	return nil
}

func parseID(s string) (int, error) {
	id, err := strconv.Atoi(s)
	if err != nil {
		return 0, fmt.Errorf("invalid task id %q", s)
	}
	return id, nil
}

func printUsage() {
	fmt.Println(`Task Tracker CLI

Usage:
  task-cli add <description>
  task-cli update <id> <description>
  task-cli delete <id>
  task-cli mark-in-progress <id>
  task-cli mark-done <id>
  task-cli list
  task-cli list done
  task-cli list todo
  task-cli list in-progress`)
}
