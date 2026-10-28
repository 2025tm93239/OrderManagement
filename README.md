# SEZG504 Assignment — Question 2 (Order API + MCP + Kong)

C# solution for Visual Studio / `dotnet` CLI.

## Projects

| Project | Purpose |
|---------|---------|
| `OrderApi` | REST API (`POST/GET /orders`) with in-memory storage |
| `OrderMcpServer` | MCP stdio server exposing the `order_api` tool |

Flow: **LLM → MCP client → MCP server → Kong (`/api/orders`) → Order API backend**

## Prerequisites

- [.NET 10 SDK](https://dotnet.microsoft.com/download) (or VS 2026 with matching SDK)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (for Kong)
- Visual Studio: open `OrderManagement.slnx`

Replace `D:\Bits-pilani\API\OrderManagement` below if your clone lives elsewhere.

## Build entire solution

```powershell
cd "D:\Bits-pilani\API\OrderManagement"
dotnet build OrderManagement.slnx
```

---

## 1. Run the Order API (backend)

### Option A — Visual Studio (recommended for testing)

1. Open `OrderManagement.slnx` in Visual Studio.
2. Right-click **OrderApi** → **Set as Startup Project**.
3. In the toolbar, select launch profile **http** (not https).
4. Press **F5** or **Ctrl+F5**.
5. Confirm the output window shows: `Now listening on: http://localhost:5280`.

Keep Visual Studio running while you test. Kong and MCP depend on this process.

### Option B — Command line

```powershell
cd "D:\Bits-pilani\API\OrderManagement\OrderApi"
dotnet run --launch-profile http
```

API listens on **http://localhost:5280**.

---

## 2. Test Part A — Direct Order API (PowerShell, no scripts)

Run these commands in PowerShell while **OrderApi** is running.

**Create order** (expect `201` and JSON with `id`, `item`, `quantity`, `status: "created"`):

```powershell
Invoke-RestMethod -Uri "http://localhost:5280/orders" -Method Post `
  -ContentType "application/json" `
  -Body '{"item":"Pen","quantity":3}'
```

**Create another order:**

```powershell
Invoke-RestMethod -Uri "http://localhost:5280/orders" -Method Post `
  -ContentType "application/json" `
  -Body '{"item":"Notebook","quantity":2}'
```

**List all orders** (expect `200` and an array):

```powershell
Invoke-RestMethod -Uri "http://localhost:5280/orders" -Method Get
```

**Get order by id** (expect `200`; use an id from create, e.g. `1`):

```powershell
Invoke-RestMethod -Uri "http://localhost:5280/orders/1" -Method Get
```

**Validation: quantity ≤ 0** (expect HTTP `400`):

```powershell
try {
  Invoke-RestMethod -Uri "http://localhost:5280/orders" -Method Post `
    -ContentType "application/json" `
    -Body '{"item":"Bad","quantity":0}'
} catch {
  $_.Exception.Response.StatusCode.value__
}
```

**Order not found** (expect HTTP `404`):

```powershell
try {
  Invoke-RestMethod -Uri "http://localhost:5280/orders/9999" -Method Get
} catch {
  $_.Exception.Response.StatusCode.value__
}
```

**Optional — status code and raw JSON body:**

```powershell
$r = Invoke-WebRequest -Uri "http://localhost:5280/orders" -Method Get -UseBasicParsing
$r.StatusCode
$r.Content
```

### PowerShell tips

| Tip | Why |
|-----|-----|
| Use single-quoted JSON in `-Body '{"item":"Pen","quantity":3}'` | Avoids escaping issues on Windows |
| Use **Invoke-RestMethod** for success cases | Parses JSON into objects |
| Use **Invoke-WebRequest** + `try/catch` for errors | Easier to read HTTP `400` / `404` / `429` |
| Avoid `curl -d` for POST on Windows | Often sends malformed JSON |

---

## 3. Start Kong (rate limit 5 req/min)

Ensure **OrderApi** from step 1 is running, then in a **separate** PowerShell window:

```powershell
cd "D:\Bits-pilani\API\OrderManagement\kong"
docker compose up -d
```

Verify the container is up:

```powershell
docker ps --filter "name=order-kong"
```

Declarative config: `kong/kong.yml` (service → `host.docker.internal:5280/orders`, route `/api/orders`, `rate-limiting` plugin, **5 requests per minute**).

If Kong fails to start (`Address already in use`):

```powershell
docker compose down
docker compose up -d
```

---

## 4. Test Part C — API via Kong (PowerShell, no scripts)

**List orders via Kong:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/orders" -Method Get
```

**Create order via Kong:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/orders" -Method Post `
  -ContentType "application/json" `
  -Body '{"item":"ViaKong","quantity":1}'
```

**Get order by id via Kong:**

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/orders/1" -Method Get
```

### Demonstrate rate limiting

For a clean counter (screenshot-friendly), restart Kong, wait a few seconds, then send 8 requests:

```powershell
cd "D:\Bits-pilani\API\OrderManagement\kong"
docker compose restart
Start-Sleep -Seconds 8

1..8 | ForEach-Object {
  try {
    $r = Invoke-WebRequest -Uri "http://localhost:8000/api/orders" -Method Get -UseBasicParsing
    "Request $_ : $($r.StatusCode)"
  } catch {
    "Request $_ : $($_.Exception.Response.StatusCode.value__)"
  }
  Start-Sleep -Milliseconds 300
}
```

Expected: requests **1–5 → `200`**, requests **6–8 → `429`** with `"API rate limit exceeded"`.

Capture a screenshot of the PowerShell output for your assignment PDF.

Optional script (same behavior): `scripts/demo-rate-limit.ps1`  
Full checklist script: `scripts/test-question2-assignment.ps1`

---

## 5. Run and test the MCP server (Part B)

`OrderMcpServer` calls the API via Kong (`OrderApi:BaseUrl` in `OrderMcpServer/appsettings.json`, default `http://localhost:8000/api/orders`).

**Start Order API and Kong first**, then:

```powershell
cd "D:\Bits-pilani\API\OrderManagement\OrderMcpServer"
dotnet run
```

Register in an MCP client (e.g. Cursor / Claude Desktop / Visual Studio) as a stdio server:

```json
{
  "mcpServers": {
    "order-api": {
      "command": "dotnet",
      "args": [
        "run",
        "--project",
        "D:/Bits-pilani/API/OrderManagement/OrderMcpServer/OrderMcpServer.csproj"
      ]
    }
  }
}
```

In chat, ask the agent to use tool **`order_api`** with:

- `create_order` — e.g. `item`: `"Book"`, `quantity`: `1`
- `get_order` — e.g. `id`: `1`
- `list_orders`

Screenshot tool calls and JSON responses for submission.

Tool schema (deliverable): `schemas/order_api-tool-schema.json`

---

## Assignment screenshot checklist

1. Visual Studio — **OrderApi** running on **http://localhost:5280**
2. PowerShell — Part A: **POST**, **GET list**, **GET by id**, **400**, **404**
3. PowerShell — Part C: **GET/POST through Kong** on **http://localhost:8000/api/orders**
4. PowerShell — rate limiting: **429** after the 5th request in a minute
5. MCP client — **`order_api`** tool: `create_order`, `get_order`, `list_orders`

---

## Submission checklist

1. `OrderApi` source  
2. `OrderMcpServer` source  
3. `schemas/order_api-tool-schema.json`  
4. `kong/kong.yml` (+ optional `kong/setup-kong-admin.ps1`)  
5. Screenshot/log of rate limiting (PowerShell commands above or `scripts/demo-rate-limit.ps1`)
