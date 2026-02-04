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

var tracesCmd = &cli.Command{
	Name:  "traces",
	Usage: "Query distributed traces",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Usage: "Time range (e.g., 24h, 7d, 2w)",
			Value: "24h",
		},
		&cli.StringFlag{
			Name:  "cluster",
			Usage: "Filter by cluster",
		},
		&cli.StringFlag{
			Name:  "service",
			Usage: "Filter by service",
		},
		&cli.StringFlag{
			Name:  "trace-id",
			Usage: "Get specific trace",
		},
		&cli.StringFlag{
			Name:  "status",
			Usage: "Filter by status (ok, error)",
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
		if v := c.String("cluster"); v != "" {
			params.Set("cluster", v)
		}
		if v := c.String("service"); v != "" {
			params.Set("service", v)
		}
		if v := c.String("trace-id"); v != "" {
			params.Set("trace_id", v)
		}
		if v := c.String("status"); v != "" {
			params.Set("status", v)
		}

		data, err := client.Query("traces", params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		traces, err := api.ParseList(data)
		if err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(traces)
		}

		if len(traces) == 0 {
			fmt.Println("No traces found")
			return nil
		}

		table := output.Table([]string{"Time", "Service", "Operation", "Duration", "Status", "Trace ID"})
		for _, t := range traces {
			ts := ""
			if v, ok := t["timestamp"].(string); ok {
				ts = output.RelativeTime(v)
			}
			svc := ""
			if v, ok := t["service_name"].(string); ok {
				svc = output.Truncate(v, 20)
			}
			op := ""
			if v, ok := t["operation"].(string); ok {
				op = output.Truncate(v, 30)
			}
			dur := ""
			if v, ok := t["duration_ms"].(float64); ok {
				dur = fmt.Sprintf("%.0fms", v)
			}
			status := ""
			if v, ok := t["status"].(string); ok {
				status = output.StatusColor(v)
			}
			traceID := ""
			if v, ok := t["trace_id"].(string); ok {
				if len(v) > 16 {
					traceID = v[:16]
				} else {
					traceID = v
				}
			}
			table.Append([]string{ts, svc, op, dur, status, traceID})
		}
		table.Render()

		return nil
	},
}
