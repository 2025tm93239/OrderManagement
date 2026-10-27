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

## 1. Run the Order API (backend)

```powershell
cd "D:\Bits-pilani\API-Based Products(SEZG504)\OrderManagement\OrderApi"
dotnet run --launch-profile http
```

API listens on **http://localhost:5280**.

Quick test:

```powershell
curl -X POST http://localhost:5280/orders -H "Content-Type: application/json" -d "{\"item\":\"Pen\",\"quantity\":3}"
curl http://localhost:5280/orders
```

## 2. Start Kong (rate limit 5 req/min)

Ensure the API from step 1 is running, then:

```powershell
cd "D:\Bits-pilani\API-Based Products(SEZG504)\OrderManagement\kong"
docker compose up -d
```

Declarative config: `kong/kong.yml` (service → `host.docker.internal:5280/orders`, route `/api/orders`, `rate-limiting` plugin).

Test through Kong:

```powershell
curl http://localhost:8000/api/orders
```

### Demonstrate rate limiting

```powershell
cd "D:\Bits-pilani\API-Based Products(SEZG504)\OrderManagement\scripts"
.\demo-rate-limit.ps1
```

Capture a screenshot when requests **6–8** return **HTTP 429**.

## 3. Run the MCP server

`OrderMcpServer` calls the API via Kong (`OrderApi:BaseUrl` in `OrderMcpServer/appsettings.json`).

```powershell
cd "D:\Bits-pilani\API-Based Products(SEZG504)\OrderManagement\OrderMcpServer"
dotnet run
```

Register in an MCP client (e.g. Cursor / Claude Desktop) as a stdio server:

```json
{
  "mcpServers": {
    "order-api": {
      "command": "dotnet",
      "args": [
        "run",
        "--project",
        "D:/Bits-pilani/API-Based Products(SEZG504)/OrderManagement/OrderMcpServer/OrderMcpServer.csproj"
      ]
    }
  }
}
```

Tool schema (deliverable): `schemas/order_api-tool-schema.json`

## Build entire solution

```powershell
cd "D:\Bits-pilani\API-Based Products(SEZG504)\OrderManagement"
dotnet build OrderManagement.slnx
```

## Submission checklist

1. `OrderApi` source  
2. `OrderMcpServer` source  
3. `schemas/order_api-tool-schema.json`  
4. `kong/kong.yml` (+ optional `kong/setup-kong-admin.ps1`)  
5. Screenshot/log of rate limiting (`scripts/demo-rate-limit.ps1`)
