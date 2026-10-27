# Sends 8 GET requests through Kong; expect HTTP 429 after the 5th request per minute.
$uri = "http://localhost:8000/api/orders"

Write-Host "Hitting $uri (rate limit: 5 requests/minute)`n"

1..8 | ForEach-Object {
    $n = $_
    try {
        $response = Invoke-WebRequest -Uri $uri -Method Get -UseBasicParsing
        Write-Host "Request $n : $($response.StatusCode)"
    }
    catch {
        $status = $_.Exception.Response.StatusCode.value__
        Write-Host "Request $n : $status"
        if ($_.ErrorDetails.Message) {
            Write-Host "  $($_.ErrorDetails.Message)"
        }
    }
    Start-Sleep -Milliseconds 200
}
