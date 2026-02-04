package cmd

import (
	"context"
	"fmt"

	"github.com/cased/cli/internal/config"
	"github.com/urfave/cli/v3"
)

var logoutCmd = &cli.Command{
	Name:  "logout",
	Usage: "Remove saved credentials",
	Action: func(ctx context.Context, c *cli.Command) error {
		if err := config.Clear(); err != nil {
			fmt.Println("No credentials found")
			return nil
		}
		fmt.Println("Logged out successfully")
		return nil
	},
}
