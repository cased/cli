package config

import (
	"os"
	"path/filepath"
	"testing"
)

func TestLoadFromEnv(t *testing.T) {
	// Set env vars
	os.Setenv("CASED_API_KEY", "test-token-123")
	os.Setenv("CASED_API_URL", "https://custom.example.com")
	defer os.Unsetenv("CASED_API_KEY")
	defer os.Unsetenv("CASED_API_URL")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() error: %v", err)
	}

	if cfg.Token != "test-token-123" {
		t.Errorf("Token = %q, want %q", cfg.Token, "test-token-123")
	}
	if cfg.APIURL != "https://custom.example.com" {
		t.Errorf("APIURL = %q, want %q", cfg.APIURL, "https://custom.example.com")
	}
}

func TestLoadDefaultAPIURL(t *testing.T) {
	// Clear env vars
	os.Unsetenv("CASED_API_KEY")
	os.Unsetenv("CASED_API_URL")

	cfg, err := Load()
	if err != nil {
		t.Fatalf("Load() error: %v", err)
	}

	if cfg.APIURL != DefaultAPIURL {
		t.Errorf("APIURL = %q, want %q", cfg.APIURL, DefaultAPIURL)
	}
}

func TestSaveAndLoad(t *testing.T) {
	// Use temp dir for config
	tmpDir := t.TempDir()
	origHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Clear env vars so file is used
	os.Unsetenv("CASED_API_KEY")
	os.Unsetenv("CASED_API_URL")

	cfg := &Config{
		Token:      "saved-token",
		APIURL:     "https://saved.example.com",
		DefaultApp: "ghostty",
	}

	if err := Save(cfg); err != nil {
		t.Fatalf("Save() error: %v", err)
	}

	// Verify file exists with correct permissions
	configPath := filepath.Join(tmpDir, ".config", "cased", "config.json")
	info, err := os.Stat(configPath)
	if err != nil {
		t.Fatalf("Config file not created: %v", err)
	}
	if info.Mode().Perm() != 0600 {
		t.Errorf("Config permissions = %o, want 0600", info.Mode().Perm())
	}

	// Load and verify
	loaded, err := Load()
	if err != nil {
		t.Fatalf("Load() error: %v", err)
	}

	if loaded.Token != cfg.Token {
		t.Errorf("Token = %q, want %q", loaded.Token, cfg.Token)
	}
	if loaded.APIURL != cfg.APIURL {
		t.Errorf("APIURL = %q, want %q", loaded.APIURL, cfg.APIURL)
	}
	if loaded.DefaultApp != cfg.DefaultApp {
		t.Errorf("DefaultApp = %q, want %q", loaded.DefaultApp, cfg.DefaultApp)
	}
}

func TestEnvOverridesFile(t *testing.T) {
	// Use temp dir for config
	tmpDir := t.TempDir()
	origHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Save config to file
	cfg := &Config{
		Token:  "file-token",
		APIURL: "https://file.example.com",
	}
	if err := Save(cfg); err != nil {
		t.Fatalf("Save() error: %v", err)
	}

	// Set env vars that should override
	os.Setenv("CASED_API_KEY", "env-token")
	os.Setenv("CASED_API_URL", "https://env.example.com")
	defer os.Unsetenv("CASED_API_KEY")
	defer os.Unsetenv("CASED_API_URL")

	loaded, err := Load()
	if err != nil {
		t.Fatalf("Load() error: %v", err)
	}

	// Env should override file
	if loaded.Token != "env-token" {
		t.Errorf("Token = %q, want %q (env should override)", loaded.Token, "env-token")
	}
	if loaded.APIURL != "https://env.example.com" {
		t.Errorf("APIURL = %q, want %q (env should override)", loaded.APIURL, "https://env.example.com")
	}
}

func TestClear(t *testing.T) {
	// Use temp dir for config
	tmpDir := t.TempDir()
	origHome := os.Getenv("HOME")
	os.Setenv("HOME", tmpDir)
	defer os.Setenv("HOME", origHome)

	// Save config
	cfg := &Config{Token: "test", APIURL: DefaultAPIURL}
	if err := Save(cfg); err != nil {
		t.Fatalf("Save() error: %v", err)
	}

	// Clear it
	if err := Clear(); err != nil {
		t.Fatalf("Clear() error: %v", err)
	}

	// Verify file is gone
	configPath := filepath.Join(tmpDir, ".config", "cased", "config.json")
	if _, err := os.Stat(configPath); !os.IsNotExist(err) {
		t.Error("Config file should be deleted after Clear()")
	}
}
