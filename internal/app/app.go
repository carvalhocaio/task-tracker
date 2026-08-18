// Package app implements the task tracker's business rules on top
// of a storage.Store. It has no knowledge of the command line --
// callers pass plain values in and get plain values or errors back.
package app

import (
	"errors"

	"github.com/carvalhocaio/task-tracker/internal/storage"
	"github.com/carvalhocaio/task-tracker/internal/task"
)

var (
	ErrTaskNotFound     = errors.New("task not found")
	ErrEmptyDescription = errors.New("description cannot be empty")
	ErrInvalidStatus    = errors.New("invalid status")
)

// App wires business rules to a persistence layer.
type App struct {
	store *storage.Store
}

// New builds an App backed by the given store.
func New(store *storage.Store) *App {
	return &App{store: store}
}

// Add creates a new task with status "todo" and persists it.
func (a *App) Add(description string) (*task.Task, error) {
	if description == "" {
		return nil, ErrEmptyDescription
	}

	tasks, err := a.store.Load()
	if err != nil {
		return nil, err
	}

	newTask := task.New(nextID(tasks), description)
	tasks = append(tasks, newTask)

	if err := a.store.Save(tasks); err != nil {
		return nil, err
	}

	return newTask, nil
}

// Update changes a task's description and refreshes its UpdatedAt.
func (a *App) Update(id int, description string) error {
	if description == "" {
		return ErrEmptyDescription
	}

	tasks, err := a.store.Load()
	if err != nil {
		return err
	}

	t := find(tasks, id)
	if t == nil {
		return ErrTaskNotFound
	}

	t.Description = description
	t.Touch()

	return a.store.Save(tasks)
}

// Delete removes a task by ID.
func (a *App) Delete(id int) error {
	tasks, err := a.store.Load()
	if err != nil {
		return err
	}

	idx := -1
	for i, t := range tasks {
		if t.ID == id {
			idx = i
			break
		}
	}

	if idx == -1 {
		return ErrTaskNotFound
	}

	tasks = append(tasks[:idx], tasks[idx+1:]...)

	return a.store.Save(tasks)
}

// SetStatus updates a task's status and refreshes its UpdatedAt.
func (a *App) SetStatus(id int, status task.Status) error {
	if !status.IsValid() {
		return ErrInvalidStatus
	}

	tasks, err := a.store.Load()
	if err != nil {
		return err
	}

	t := find(tasks, id)
	if t == nil {
		return ErrTaskNotFound
	}

	t.Status = status
	t.Touch()

	return a.store.Save(tasks)
}

// List returns all tasks, or only those matching filter when it's non-empty
func (a *App) List(filter task.Status) ([]*task.Task, error) {
	tasks, err := a.store.Load()
	if err != nil {
		return nil, err
	}

	if filter == "" {
		return tasks, nil
	}

	filtered := make([]*task.Task, 0, len(tasks))
	for _, t := range tasks {
		if t.Status == filter {
			filtered = append(filtered, t)
		}
	}

	return filtered, nil
}

func find(tasks []*task.Task, id int) *task.Task {
	for _, t := range tasks {
		if t.ID == id {
			return t
		}
	}
	return nil
}

// nextID returns the smallest unused, ever-increasing ID.
// Note: this assumes a single process writing at a time -- fine for
// a local CLI tool, but not safe for concurrent access.
func nextID(tasks []*task.Task) int {
	maxID := 0
	for _, t := range tasks {
		if t.ID > maxID {
			maxID = t.ID
		}
	}
	return maxID + 1
}
