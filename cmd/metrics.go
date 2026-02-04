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

var metricsCmd = &cli.Command{
	Name:  "metrics",
	Usage: "Query container metrics",
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
			Name:  "namespace",
			Usage: "Filter by namespace",
		},
		&cli.StringFlag{
			Name:  "pod",
			Usage: "Filter by pod name",
		},
		&cli.StringFlag{
			Name:  "metric",
			Usage: "Metric name (cpu, memory)",
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
		if v := c.String("namespace"); v != "" {
			params.Set("namespace", v)
		}
		if v := c.String("pod"); v != "" {
			params.Set("pod", v)
		}
		if v := c.String("metric"); v != "" {
			params.Set("metric", v)
		}

		data, err := client.Query("metrics", params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		metrics, err := api.ParseList(data)
		if err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(metrics)
		}

		if len(metrics) == 0 {
			fmt.Println("No metrics found")
			return nil
		}

		table := output.Table([]string{"Time", "Pod", "Namespace", "CPU", "Memory"})
		for _, m := range metrics {
			ts := ""
			if v, ok := m["timestamp"].(string); ok {
				ts = output.RelativeTime(v)
			}
			pod := ""
			if v, ok := m["pod_name"].(string); ok {
				pod = output.Truncate(v, 30)
			}
			ns := ""
			if v, ok := m["namespace"].(string); ok {
				ns = v
			}
			cpu := ""
			if v, ok := m["cpu_percent"].(float64); ok {
				cpu = fmt.Sprintf("%.1f%%", v)
			}
			mem := ""
			if v, ok := m["memory_mb"].(float64); ok {
				mem = fmt.Sprintf("%.0fMB", v)
			}
			table.Append([]string{ts, pod, ns, cpu, mem})
		}
		table.Render()

		return nil
	},
}
