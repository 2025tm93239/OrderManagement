# Optional: configure Kong via Admin API (DB mode). For this assignment, prefer docker-compose + kong.yml.
$admin = "http://localhost:8001"

$serviceBody = @{
    name = "order-api-service"
    url  = "http://host.docker.internal:5280/orders"
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$admin/services" -Body $serviceBody -ContentType "application/json"

$routeBody = @{
    name       = "order-api-route"
    paths      = @("/api/orders")
    strip_path = $true
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$admin/services/order-api-service/routes" -Body $routeBody -ContentType "application/json"

$pluginBody = @{
    name   = "rate-limiting"
    config = @{
        minute   = 5
        policy   = "local"
        limit_by = "ip"
    }
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri "$admin/services/order-api-service/plugins" -Body $pluginBody -ContentType "application/json"

Write-Host "Kong service, route /api/orders, and rate limiting (5/min) configured."
