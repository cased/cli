package cmd

import (
	"context"
	"fmt"
	"net/url"
	"os"
	"os/signal"
	"time"

	"github.com/cased/cli/internal/api"
	"github.com/cased/cli/internal/config"
	"github.com/cased/cli/internal/output"
	"github.com/urfave/cli/v3"
)

var logsCmd = &cli.Command{
	Name:  "logs",
	Usage: "Query application logs",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Usage: "Time range (e.g., 24h, 7d, 2w)",
			Value: "24h",
		},
		&cli.IntFlag{
			Name:  "tail",
			Usage: "Show last N logs",
			Value: 50,
		},
		&cli.StringFlag{
			Name:  "level",
			Usage: "Filter by level",
		},
		&cli.StringFlag{
			Name:  "service",
			Usage: "Filter by service",
		},
		&cli.StringFlag{
			Name:  "search",
			Usage: "Search in messages",
		},
		&cli.BoolFlag{
			Name:    "follow",
			Aliases: []string{"f"},
			Usage:   "Follow logs in real-time",
		},
		&cli.BoolFlag{
			Name:    "timestamps",
			Aliases: []string{"t"},
			Usage:   "Show timestamps",
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
		params.Set("limit", fmt.Sprintf("%d", c.Int("tail")))
		if v := c.String("level"); v != "" {
			params.Set("level", v)
		}
		if v := c.String("service"); v != "" {
			params.Set("service", v)
		}
		if v := c.String("search"); v != "" {
			params.Set("search", v)
		}

		showTimestamps := c.Bool("timestamps")

		if c.Bool("follow") {
			return followLogs(ctx, client, params, showTimestamps)
		}

		data, err := client.Query("logs", params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		logs, err := api.ParseList(data)
		if err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(logs)
		}

		for _, log := range logs {
			printLog(log, showTimestamps)
		}

		return nil
	},
}

func printLog(log map[string]any, showTimestamps bool) {
	var line string

	if showTimestamps {
		if ts, ok := log["timestamp"].(string); ok {
			line += output.Dim(output.FormatTime(ts)) + " "
		}
	}

	if level, ok := log["level"].(string); ok {
		line += output.LevelColor(level) + " "
	}

	if svc, ok := log["service"].(string); ok {
		line += output.Blue("["+svc+"]") + " "
	}

	if msg, ok := log["message"].(string); ok {
		line += msg
	}

	fmt.Println(line)
}

func followLogs(ctx context.Context, client *api.Client, params url.Values, showTimestamps bool) error {
	seenIDs := make(map[string]bool)

	// Handle Ctrl+C
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt)

	fmt.Println(output.Dim("Following logs... (Ctrl+C to stop)"))

	ticker := time.NewTicker(2 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-sigCh:
			fmt.Println(output.Dim("\nStopped"))
			return nil
		case <-ticker.C:
			data, err := client.Query("logs", params)
			if err != nil {
				continue
			}

			logs, err := api.ParseList(data)
			if err != nil {
				continue
			}

			currentIDs := make(map[string]bool)
			for _, log := range logs {
				if id, ok := log["log_id"].(string); ok {
					currentIDs[id] = true
					if !seenIDs[id] {
						printLog(log, showTimestamps)
						seenIDs[id] = true
					}
				}
			}

			// Prevent memory growth
			if len(seenIDs) > 1000 {
				seenIDs = currentIDs
			}
		}
	}
}
