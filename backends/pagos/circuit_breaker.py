import pybreaker

http_breaker = pybreaker.CircuitBreaker(
    fail_max=3,
    reset_timeout=30,
    name="http_inter_service"
)
