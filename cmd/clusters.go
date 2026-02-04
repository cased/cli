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

var clustersCmd = &cli.Command{
	Name:  "clusters",
	Usage: "List clusters with telemetry data",
	Flags: []cli.Flag{
		&cli.StringFlag{
			Name:  "since",
			Usage: "Time range (e.g., 24h, 7d, 2w)",
			Value: "24h",
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

		data, err := client.Query("clusters", params)
		if err != nil {
			return exitError("Query failed: %v", err)
		}

		clusters, err := api.ParseList(data)
		if err != nil {
			return exitError("Failed to parse response: %v", err)
		}

		if jsonOutput {
			return output.JSON(clusters)
		}

		if len(clusters) == 0 {
			fmt.Println("No clusters found")
			return nil
		}

		table := output.Table([]string{"Cluster", "Namespaces", "Pods", "Last Seen"})
		for _, cl := range clusters {
			name := ""
			if v, ok := cl["cluster_name"].(string); ok {
				name = v
			}
			ns := ""
			if v, ok := cl["namespace_count"].(float64); ok {
				ns = fmt.Sprintf("%.0f", v)
			}
			pods := ""
			if v, ok := cl["pod_count"].(float64); ok {
				pods = fmt.Sprintf("%.0f", v)
			}
			lastSeen := ""
			if v, ok := cl["last_seen"].(string); ok {
				lastSeen = output.RelativeTime(v)
			}
			table.Append([]string{name, ns, pods, lastSeen})
		}
		table.Render()

		return nil
	},
}
