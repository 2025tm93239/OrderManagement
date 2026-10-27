using OrderApi.Models;

namespace OrderApi.Services;

public sealed class OrderStore
{
    private readonly object _lock = new();
    private int _nextId = 1;
    private readonly Dictionary<int, Order> _orders = new();

    public Order Create(string item, int quantity)
    {
        lock (_lock)
        {
            var order = new Order(_nextId++, item, quantity, "created");
            _orders[order.Id] = order;
            return order;
        }
    }

    public Order? GetById(int id) =>
        _orders.TryGetValue(id, out var order) ? order : null;

    public IReadOnlyList<Order> GetAll()
    {
        lock (_lock)
        {
            return _orders.Values.OrderBy(o => o.Id).ToList();
        }
    }
}
