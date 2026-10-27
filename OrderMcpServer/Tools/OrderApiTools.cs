using System.ComponentModel;
using System.Net.Http.Json;
using System.Text.Json;
using Microsoft.Extensions.Configuration;
using ModelContextProtocol.Server;

namespace OrderMcpServer.Tools;

internal sealed class OrderApiTools
{
    private static readonly HashSet<string> ValidActions =
        ["create_order", "get_order", "list_orders"];

    private readonly HttpClient _httpClient;
    private readonly string _baseUrl;

    public OrderApiTools(HttpClient httpClient, IConfiguration configuration)
    {
        _httpClient = httpClient;
        _baseUrl = configuration["OrderApi:BaseUrl"]?.TrimEnd('/')
            ?? "http://localhost:8000/api/orders";
    }

    [McpServerTool(Name = "order_api")]
    [Description(
        "Order API tool. Actions: create_order (item, quantity), get_order (id), list_orders.")]
    public async Task<string> OrderApi(
        [Description("One of: create_order, get_order, list_orders")] string action,
        [Description("Order item name (required for create_order)")] string? item = null,
        [Description("Order quantity (required for create_order, must be > 0)")] int? quantity = null,
        [Description("Order id (required for get_order)")] int? id = null,
        CancellationToken cancellationToken = default)
    {
        if (string.IsNullOrWhiteSpace(action) || !ValidActions.Contains(action))
        {
            return JsonSerializer.Serialize(new
            {
                error = "Invalid action. Use create_order, get_order, or list_orders."
            });
        }

        return action switch
        {
            "create_order" => await CreateOrderAsync(item, quantity, cancellationToken),
            "get_order" => await GetOrderAsync(id, cancellationToken),
            "list_orders" => await ListOrdersAsync(cancellationToken),
            _ => JsonSerializer.Serialize(new { error = "Unsupported action." })
        };
    }

    private async Task<string> CreateOrderAsync(string? item, int? quantity, CancellationToken cancellationToken)
    {
        if (string.IsNullOrWhiteSpace(item))
        {
            return JsonSerializer.Serialize(new { error = "item is required for create_order." });
        }

        if (quantity is null or <= 0)
        {
            return JsonSerializer.Serialize(new { error = "quantity must be greater than 0 for create_order." });
        }

        using var response = await _httpClient.PostAsJsonAsync(
            _baseUrl,
            new { item = item.Trim(), quantity = quantity.Value },
            cancellationToken);

        return await response.Content.ReadAsStringAsync(cancellationToken);
    }

    private async Task<string> GetOrderAsync(int? id, CancellationToken cancellationToken)
    {
        if (id is null or < 1)
        {
            return JsonSerializer.Serialize(new { error = "id must be greater than 0 for get_order." });
        }

        using var response = await _httpClient.GetAsync($"{_baseUrl}/{id.Value}", cancellationToken);
        return await response.Content.ReadAsStringAsync(cancellationToken);
    }

    private async Task<string> ListOrdersAsync(CancellationToken cancellationToken)
    {
        using var response = await _httpClient.GetAsync(_baseUrl, cancellationToken);
        return await response.Content.ReadAsStringAsync(cancellationToken);
    }
}
