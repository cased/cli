package cmd

import (
	"context"
	"fmt"

	"github.com/urfave/cli/v3"
)

const Version = "0.4.0"

var jsonOutput bool

func Run(ctx context.Context, args []string) error {
	app := &cli.Command{
		Name:    "cased",
		Usage:   "CLI for Cased - designed for agents, not humans",
		Version: Version,
		Flags: []cli.Flag{
			&cli.BoolFlag{
				Name:        "json",
				Aliases:     []string{"j"},
				Usage:       "Output as JSON",
				Destination: &jsonOutput,
			},
		},
		Commands: []*cli.Command{
			configureCmd,
			logoutCmd,
			errorsCmd,
			logsCmd,
			tracesCmd,
			metricsCmd,
			statsCmd,
			clustersCmd,
			sessionsCmd,
			sessionCmd,
			investigateCmd,
			docsCmd,
			sourcemapsCmd,
			perfCmd,
			llmCmd,
			setAppCmd,
		},
	}

	return app.Run(ctx, args)
}

func exitError(format string, args ...any) error {
	return cli.Exit(fmt.Sprintf(format, args...), 1)
}
