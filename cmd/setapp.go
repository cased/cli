package cmd

import (
	"context"
	"fmt"

	"github.com/cased/cli/internal/config"
	"github.com/urfave/cli/v3"
)

var supportedApps = []string{"terminal", "ghostty"}

var setAppCmd = &cli.Command{
	Name:      "set-app",
	Usage:     "Set default app for cased:// URLs",
	ArgsUsage: "[app_name]",
	Description: `Supported apps: terminal (default), ghostty

Examples:
  cased set-app ghostty    # Set Ghostty as default
  cased set-app terminal   # Reset to Terminal.app
  cased set-app            # Show current setting`,
	Action: func(ctx context.Context, c *cli.Command) error {
		cfg, err := config.Load()
		if err != nil {
			cfg = &config.Config{APIURL: config.DefaultAPIURL}
		}

		if c.NArg() < 1 {
			// Show current setting
			current := cfg.DefaultApp
			if current == "" {
				current = "terminal"
			}
			fmt.Printf("Current default app: %s\n", current)
			fmt.Printf("\nSupported apps: %v\n", supportedApps)
			fmt.Println("You can also override per-URL with ?app=ghostty")
			return nil
		}

		appName := c.Args().Get(0)

		// Validate
		valid := false
		for _, a := range supportedApps {
			if a == appName {
				valid = true
				break
			}
		}
		if !valid {
			return exitError("Unknown app: %s\nSupported: %v", appName, supportedApps)
		}

		cfg.DefaultApp = appName
		if err := config.Save(cfg); err != nil {
			return exitError("Failed to save config: %v", err)
		}

		fmt.Printf("Default app set to: %s\n", appName)
		fmt.Printf("cased:// URLs will now open in %s\n", appName)

		return nil
	},
}
