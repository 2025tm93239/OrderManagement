using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using OrderMcpServer.Tools;

var builder = Host.CreateApplicationBuilder(args);

builder.Logging.AddConsole(o => o.LogToStandardErrorThreshold = LogLevel.Trace);

builder.Services.AddHttpClient<OrderApiTools>();
builder.Services
    .AddMcpServer()
    .WithStdioServerTransport()
    .WithTools<OrderApiTools>();

await builder.Build().RunAsync();
