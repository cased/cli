package cmd

import (
	"context"
	"fmt"
	"net/url"

	"github.com/cased/cli/internal/api"
	"github.com/cased/cli/internal/config"
	"github.com/cased/cli/internal/output"
	"github.com/urfave/cli/v3"
)

var errorsCmd = &cli.Command{
	Name:  "errors",
	Usage: "Query error events",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Usage: "Time range (e.g., 24h, 7d, 2w)",
			Value: "24h",
		},
		&cli.StringFlag{
			Name:  "level",
			Usage: "Filter by level (error, warning)",
		},
		&cli.StringFlag{
			Name:  "search",
			Usage: "Search in error messages",
		},
		&cli.StringFlag{
			Name:  "project",
			Usage: "Filter by project",
		},
		&cli.IntFlag{
			Name:  "limit",
			Usage: "Max results",
			Value: 50,
		},
	},
	Action: func(ctx context.Context, c *cli.Command) error {
		cfg := config.MustLoad()
		client := api.NewClient(cfg)

		hours, err := output.ParseSince(c.String("since"))
		if err != nil {
			return exitError("Invalid --since: %v", err)
		}

		params := url.Values{}
		params.Set("hours", fmt.Sprintf("%d", hours))
		params.Set("limit", fmt.Sprintf("%d", c.Int("limit")))
		if v := c.String("level"); v != "" {
			params.Set("level", v)
		}
		if v := c.String("search"); v != "" {
			params.Set("search", v)
		}
		if v := c.String("project"); v != "" {
			params.Set("project", v)
		}

		data, err := client.Query("errors", params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		errors, err := api.ParseList(data)
		if err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(errors)
		}

		if len(errors) == 0 {
			fmt.Println("No errors found")
			return nil
		}

		table := output.Table([]string{"Time", "Level", "Type", "Message", "ID"})
		for _, e := range errors {
			ts := ""
			if t, ok := e["timestamp"].(string); ok {
				ts = output.RelativeTime(t)
			}
			level := ""
			if l, ok := e["level"].(string); ok {
				level = output.LevelColor(l)
			}
			typ := ""
			if t, ok := e["exception_type"].(string); ok {
				typ = output.Truncate(t, 30)
			}
			msg := ""
			if m, ok := e["exception_value"].(string); ok {
				msg = output.Truncate(m, 50)
			}
			id := ""
			if i, ok := e["event_id"].(string); ok {
				id = i[:8]
			}
			table.Append([]string{ts, level, typ, msg, id})
		}
		table.Render()

		return nil
	},
}
