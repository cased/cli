package cmd

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"

	"github.com/cased/cli/internal/config"
	"github.com/pkg/browser"
	"github.com/urfave/cli/v3"
)

var configureCmd = &cli.Command{
	Name:  "configure",
	Usage: "Authenticate with Cased",
	Flags: []cli.Flag{
		&cli.BoolFlag{
			Name:  "force",
			Usage: "Force re-authentication",
		},
		&cli.StringFlag{
			Name:  "api-url",
			Usage: "API URL",
			Value: config.DefaultAPIURL,
		},
	},
	Action: func(ctx context.Context, c *cli.Command) error {
		apiURL := c.String("api-url")

		// Check existing config
		if !c.Bool("force") {
			cfg, _ := config.Load()
			if cfg != nil && cfg.Token != "" {
				fmt.Println("Already authenticated. Use --force to re-authenticate.")
				return nil
			}
		}

		// Initiate device code flow
		resp, err := http.Post(apiURL+"/api/v1/cli/auth/initiate", "application/json", nil)
		if err != nil {
			return exitError("Failed to initiate auth: %v", err)
		}
		defer resp.Body.Close()

		body, _ := io.ReadAll(resp.Body)
		if resp.StatusCode != 200 {
			return exitError("Auth initiation failed: %s", string(body))
		}

		var authResp struct {
			DeviceCode      string `json:"device_code"`
			UserCode        string `json:"user_code"`
			VerificationURI string `json:"verification_uri"`
		}
		if err := json.Unmarshal(body, &authResp); err != nil {
			return exitError("Failed to parse auth response: %v", err)
		}

		fmt.Printf("Opening browser to authenticate...\n")
		fmt.Printf("Code: %s\n", authResp.UserCode)

		_ = browser.OpenURL(authResp.VerificationURI)

		// Poll for completion
		fmt.Println("Waiting for authentication...")
		pollURL := fmt.Sprintf("%s/api/v1/cli/auth/poll?device_code=%s", apiURL, authResp.DeviceCode)

		for {
			time.Sleep(2 * time.Second)

			pollResp, err := http.Get(pollURL)
			if err != nil {
				continue
			}

			pollBody, _ := io.ReadAll(pollResp.Body)
			pollResp.Body.Close()

			var pollResult struct {
				Status string `json:"status"`
				Token  string `json:"token"`
			}
			if err := json.Unmarshal(pollBody, &pollResult); err != nil {
				continue
			}

			if pollResult.Status == "complete" && pollResult.Token != "" {
				cfg := &config.Config{
					Token:  pollResult.Token,
					APIURL: apiURL,
				}
				if err := config.Save(cfg); err != nil {
					return exitError("Failed to save config: %v", err)
				}

				fmt.Println("\nSuccessfully authenticated!")
				fmt.Printf("Config saved to %s\n", config.ConfigFile())
				return nil
			}

			if pollResp.StatusCode == 400 {
				return exitError("Authentication failed or timed out")
			}
		}
	},
}
