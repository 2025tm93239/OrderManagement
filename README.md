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

## Question 2 — assignment parts

| Part | What you build | How you test (this README) |
|------|----------------|----------------------------|
| **A** | REST Order API (`POST/GET /orders`) | [§2](#2-test-part-a--direct-order-api-powershell-no-scripts) — PowerShell on **5280** |
| **B** | MCP tool `order_api` | [§5](#5-run-and-test-the-mcp-server-part-b) — MCP client + Kong + API running |
| **C** | Kong route `/api/orders`, rate limit **5/min** | [§3](#3-start-kong-rate-limit-5-reqmin), [§4](#4-test-part-c--api-via-kong-powershell-no-scripts) — PowerShell on **8000** |
| **D** | Deliverables (code, schema, Kong YAML, screenshots) | [Screenshot checklist](#assignment-screenshot-checklist), [Submission checklist](#submission-checklist) |

## Instructions to compile and run (for submission PDF)

1. Open `OrderManagement.slnx` in Visual Studio (or use CLI below).
2. Build: **Build → Build Solution** or `dotnet build OrderManagement.slnx`.
3. Run **OrderApi** with profile **http** (see [§1](#1-run-the-order-api-backend)).
4. Start Kong: `docker compose up -d` in the `kong` folder (see [§3](#3-start-kong-rate-limit-5-reqmin)).
5. Test REST endpoints with PowerShell ([§2](#2-test-part-a--direct-order-api-powershell-no-scripts), [§4](#4-test-part-c--api-via-kong-powershell-no-scripts)).
6. Register and exercise **OrderMcpServer** in an MCP client ([§5](#5-run-and-test-the-mcp-server-part-b)).
7. Capture screenshots listed in [Assignment screenshot checklist](#assignment-screenshot-checklist).

Keep the **OrderApi** process running in Visual Studio (or a dedicated terminal). Do not stop it while testing Kong or MCP.

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

**Validation: missing or empty item** (expect HTTP `400`):

```powershell
try {
  Invoke-RestMethod -Uri "http://localhost:5280/orders" -Method Post `
    -ContentType "application/json" `
    -Body '{"item":"","quantity":1}'
} catch {
  $_.Exception.Response.StatusCode.value__
}
```

**Invalid id on GET** (expect HTTP `400` if your API rejects `id < 1`):

```powershell
try {
  Invoke-RestMethod -Uri "http://localhost:5280/orders/0" -Method Get
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

**Prerequisites:** Order API on **5280** and Kong on **8000** must both be running. Verify Kong before MCP:

```powershell
Invoke-RestMethod -Uri "http://localhost:8000/api/orders" -Method Get
```

**Start Order API and Kong first**, then:

```powershell
cd "D:\Bits-pilani\API\OrderManagement\OrderMcpServer"
dotnet run
```

**Visual Studio:** use MCP configuration (solution `.mcp.json` or VS MCP settings) with the same `dotnet run --project` args as below.

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

---

## Demo video

Local file: [`Screenshots and Demo video/Question 2 Short Demos Recording.mp4`](./Screenshots%20and%20Demo%20video/Question%202%20Short%20Demos%20Recording.mp4)

After you push to GitHub, open the `.mp4` from the repo file view to stream or download. For a shareable link in reports, upload the same file to Drive/OneDrive and paste that URL here if needed.

## Screenshots

Folder: [`Screenshots and Demo video/`](./Screenshots%20and%20Demo%20video/)

| | |
|:---:|:---:|
| ![Picture 9](./Screenshots%20and%20Demo%20video/Picture9.png) | ![Picture 10](./Screenshots%20and%20Demo%20video/Picture10.png) |
| ![Picture 11](./Screenshots%20and%20Demo%20video/Picture11.png) | ![Picture 12](./Screenshots%20and%20Demo%20video/Picture12.png) |
| ![Picture 13](./Screenshots%20and%20Demo%20video/Picture13.png) | ![Picture 14](./Screenshots%20and%20Demo%20video/Picture14.png) |
| ![Picture 15](./Screenshots%20and%20Demo%20video/Picture15.png) | ![Picture 16](./Screenshots%20and%20Demo%20video/Picture16.png) |
| ![Picture 17](./Screenshots%20and%20Demo%20video/Picture17.png) | ![Picture 18](./Screenshots%20and%20Demo%20video/Picture18.png) |
| ![Picture 19](./Screenshots%20and%20Demo%20video/Picture19.png) | ![Picture 20](./Screenshots%20and%20Demo%20video/Picture20.png) |
| ![Picture 21](./Screenshots%20and%20Demo%20video/Picture21.png) | ![Picture 22](./Screenshots%20and%20Demo%20video/Picture22.png) |
| ![Picture 23](./Screenshots%20and%20Demo%20video/Picture23.png) | ![Picture 24](./Screenshots%20and%20Demo%20video/Picture24.png) |

![Picture 25](./Screenshots%20and%20Demo%20video/Picture25.png)

![Picture 34](./Screenshots%20and%20Demo%20video/Picture34.png)
