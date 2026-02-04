package api

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/url"
	"time"

	"github.com/cased/cli/internal/config"
)

type Client struct {
	cfg        *config.Config
	httpClient *http.Client
}

func NewClient(cfg *config.Config) *Client {
	return &Client{
		cfg: cfg,
		httpClient: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// Query calls the telemetry API.
func (c *Client) Query(endpoint string, params url.Values) ([]byte, error) {
	u := fmt.Sprintf("%s/api/v1/telemetry/query/%s/", c.cfg.APIURL, endpoint)
	if len(params) > 0 {
		u += "?" + params.Encode()
	}
	return c.get(u)
}

// Agent calls the agent API.
func (c *Client) Agent(endpoint string, params url.Values) ([]byte, error) {
	u := fmt.Sprintf("%s/api/v1/agent/%s", c.cfg.APIURL, endpoint)
	if len(params) > 0 {
		u += "?" + params.Encode()
	}
	return c.get(u)
}

func (c *Client) get(u string) ([]byte, error) {
	req, err := http.NewRequest("GET", u, nil)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+c.cfg.Token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	return body, nil
}

// Post sends a POST request with JSON body.
func (c *Client) Post(u string, data any) ([]byte, error) {
	var body io.Reader
	if data != nil {
		jsonData, err := json.Marshal(data)
		if err != nil {
			return nil, err
		}
		body = bytes.NewReader(jsonData)
	}

	req, err := http.NewRequest("POST", u, body)
	if err != nil {
		return nil, err
	}
	req.Header.Set("Authorization", "Bearer "+c.cfg.Token)
	req.Header.Set("Content-Type", "application/json")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	if resp.StatusCode >= 400 {
		return nil, fmt.Errorf("API error %d: %s", resp.StatusCode, string(respBody))
	}

	return respBody, nil
}

// ParseList handles API responses that can be either:
// - A raw array: [...]
// - A paginated object: {"results": [...], "count": N}
func ParseList(data []byte) ([]map[string]any, error) {
	// Try array first
	var arr []map[string]any
	if err := json.Unmarshal(data, &arr); err == nil {
		return arr, nil
	}

	// Try paginated object
	var paginated struct {
		Results []map[string]any `json:"results"`
		Count   int              `json:"count"`
	}
	if err := json.Unmarshal(data, &paginated); err == nil {
		return paginated.Results, nil
	}

	// Return raw error
	return nil, fmt.Errorf("unexpected response format: %s", string(data[:min(100, len(data))]))
}

// Delete sends a DELETE request.
func (c *Client) Delete(u string) error {
	req, err := http.NewRequest("DELETE", u, nil)
	if err != nil {
		return err
	}
	req.Header.Set("Authorization", "Bearer "+c.cfg.Token)

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if resp.StatusCode >= 400 {
		body, _ := io.ReadAll(resp.Body)
		return fmt.Errorf("API error %d: %s", resp.StatusCode, string(body))
	}

	return nil
}
