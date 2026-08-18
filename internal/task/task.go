// Package task defines the Task entity and its possible statuses.
package task

import "time"

// Status represents the lifecycle state of a Task.
type Status string

const (
	StatusTodo       Status = "todo"
	StatusInProgress Status = "in-progress"
	StatusDone       Status = "done"
)

// IsValid reports whether s is one of the known statuses.
func (s Status) IsValid() bool {
	switch s {
	case StatusTodo, StatusInProgress, StatusDone:
		return true
	default:
		return false
	}
}

// Task represents a single to-do item persisted to disk.
type Task struct {
	ID          int       `json:"id"`
	Description string    `json:"description"`
	Status      Status    `json:"status"`
	CreatedAt   time.Time `json:"createdAt"`
	UpdatedAt   time.Time `json:"updatedAt"`
}

// New creates a Task with status "todo" and both time stamps set to now.
func New(id int, description string) *Task {
	now := time.Now()
	return &Task{
		ID:          id,
		Description: description,
		Status:      StatusTodo,
		CreatedAt:   now,
		UpdatedAt:   now,
	}
}

// Touch updates UpdatedAt to the current time. Call this whenever
// a task's mutable fields (description, status) change.
func (t *Task) Touch() {
	t.UpdatedAt = time.Now()
}
