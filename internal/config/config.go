package config

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

const DefaultAPIURL = "https://app.cased.com"

type Config struct {
	Token      string `json:"token"`
	APIURL     string `json:"api_url"`
	DefaultApp string `json:"default_app,omitempty"`
}

func configDir() string {
	home, _ := os.UserHomeDir()
	return filepath.Join(home, ".config", "cased")
}

func ConfigFile() string {
	return filepath.Join(configDir(), "config.json")
}

// Load reads config from file, falling back to environment variables.
func Load() (*Config, error) {
	cfg := &Config{
		APIURL: DefaultAPIURL,
	}

	// Try loading from file
	data, err := os.ReadFile(ConfigFile())
	if err == nil {
		if err := json.Unmarshal(data, cfg); err != nil {
			return nil, err
		}
	}

	// Environment variables override file config
	if token := os.Getenv("CASED_API_KEY"); token != "" {
		cfg.Token = token
	}
	if url := os.Getenv("CASED_API_URL"); url != "" {
		cfg.APIURL = url
	}

	return cfg, nil
}

// MustLoad loads config and returns it, or exits if not authenticated.
func MustLoad() *Config {
	cfg, err := Load()
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error loading config: %v\n", err)
		os.Exit(1)
	}
	if cfg.Token == "" {
		fmt.Fprintln(os.Stderr, "Not authenticated. Run 'cased configure' first.")
		os.Exit(1)
	}
	return cfg
}

// Save writes config to file with secure permissions.
func Save(cfg *Config) error {
	dir := configDir()
	if err := os.MkdirAll(dir, 0700); err != nil {
		return err
	}

	data, err := json.MarshalIndent(cfg, "", "  ")
	if err != nil {
		return err
	}

	file := ConfigFile()
	if err := os.WriteFile(file, data, 0600); err != nil {
		return err
	}

	return nil
}

// Clear removes the config file.
func Clear() error {
	return os.Remove(ConfigFile())
}
