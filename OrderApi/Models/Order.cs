namespace OrderApi.Models;

public sealed record Order(int Id, string Item, int Quantity, string Status);

public sealed record CreateOrderRequest(string Item, int Quantity);
