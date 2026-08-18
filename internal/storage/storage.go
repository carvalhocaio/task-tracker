// Package storage persists tasks to JSON file on disk.
// It knows nothing about CLI parsing or business rules -- only
// how to load and save a slice of *task.Task.
package storage

import (
	"encoding/json"
	"fmt"
	"os"

	"github.com/carvalhocaio/task-tracker/internal/task"
)

const fileName = "tasks.json"

// Store reads and writes tasks to a JSON file in the current directory.
type Store struct {
	path string
}

// New returns a Store pointed at the default tasks.json path
func New() *Store {
	return &Store{path: fileName}
}

// Load reads all tasks from disk. If the file doesn't exist yet,
// it returns an empty slice (the file is created lazily on first Save).
func (s *Store) Load() ([]*task.Task, error) {
	data, err := os.ReadFile(s.path)
	if err != nil {
		if os.IsNotExist(err) {
			return []*task.Task{}, nil
		}
		return nil, fmt.Errorf("failed to read %s: %w", s.path, err)
	}

	if len(data) == 0 {
		return []*task.Task{}, nil
	}

	var tasks []*task.Task
	if err := json.Unmarshal(data, &tasks); err != nil {
		return nil, fmt.Errorf("%s is corrupted or not valid JSON: %w", s.path, err)
	}

	return tasks, nil
}

// Save writes the full task list back to disk, creating the file
// if it doesn't exist yet.
func (s *Store) Save(tasks []*task.Task) error {
	data, err := json.MarshalIndent(tasks, "", " ")
	if err != nil {
		return fmt.Errorf("failed to encode tasks: %w", err)
	}

	if err := os.WriteFile(s.path, data, 0644); err != nil {
		return fmt.Errorf("failed to write %s: %w", s.path, err)
	}

	return nil
}
