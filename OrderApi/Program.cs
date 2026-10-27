using OrderApi.Models;
using OrderApi.Services;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddSingleton<OrderStore>();
builder.Services.AddOpenApi();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.MapPost("/orders", (CreateOrderRequest request, OrderStore store) =>
{
    if (string.IsNullOrWhiteSpace(request.Item))
    {
        return Results.BadRequest(new { error = "item is required." });
    }

    if (request.Quantity <= 0)
    {
        return Results.BadRequest(new { error = "quantity must be greater than 0." });
    }

    var order = store.Create(request.Item.Trim(), request.Quantity);
    return Results.Created($"/orders/{order.Id}", order);
});

app.MapGet("/orders/{id:int}", (int id, OrderStore store) =>
{
    if (id < 1)
    {
        return Results.BadRequest(new { error = "id must be greater than 0." });
    }

    var order = store.GetById(id);
    return order is null
        ? Results.NotFound(new { error = $"order {id} was not found." })
        : Results.Ok(order);
});

app.MapGet("/orders", (OrderStore store) => Results.Ok(store.GetAll()));

app.Run();
