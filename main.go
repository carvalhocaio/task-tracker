package main

import (
	"os"

	"github.com/carvalhocaio/task-tracker/internal/app"
	"github.com/carvalhocaio/task-tracker/internal/cli"
	"github.com/carvalhocaio/task-tracker/internal/storage"
)

func main() {
	a := app.New(storage.New())
	os.Exit(cli.Run(a, os.Args[1:]))
}
