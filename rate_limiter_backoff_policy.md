# Rate Limiter & Backoff Policy

- **Retryable:** 429, 500, 502.
- **Non-Retryable:** 401, 404.
- **Backoff:** Bounded Exponential (1000ms base, 30000ms max) with Jitter.
- **Retry Ceiling:** 3 retries max.
