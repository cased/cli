package main

import (
	"context"
	"os"

	"github.com/cased/cli/cmd"
)

func main() {
	if err := cmd.Run(context.Background(), os.Args); err != nil {
		os.Exit(1)
	}
}
