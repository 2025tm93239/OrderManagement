# Register Order API service, route /api/orders, and rate limiting (5 req/min).
$KongAdmin = if ($env:KONG_ADMIN) { $env:KONG_ADMIN } else { "http://127.0.0.1:8002" }
$Upstream = if ($env:UPSTREAM) { $env:UPSTREAM } else { "http://host.docker.internal:8001/orders" }

Write-Host "Kong Admin: $KongAdmin"
Write-Host "Upstream:   $Upstream"

Invoke-RestMethod -Method Post -Uri "$KongAdmin/services" -Body @{
    name = "order-api-service"
    url  = $Upstream
} | ConvertTo-Json -Depth 5

$service = Invoke-RestMethod -Uri "$KongAdmin/services/order-api-service"
$serviceId = $service.id

Invoke-RestMethod -Method Post -Uri "$KongAdmin/services/$serviceId/routes" -Body @{
    name       = "orders-route"
    "paths[]"  = "/api/orders"
    strip_path = "true"
    "methods[]" = @("GET", "POST")
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post -Uri "$KongAdmin/services/$serviceId/plugins" -Body @{
    name              = "rate-limiting"
    "config.minute"   = "5"
    "config.policy"   = "local"
    "config.limit_by" = "ip"
} | ConvertTo-Json -Depth 5

Write-Host "Kong setup complete."
