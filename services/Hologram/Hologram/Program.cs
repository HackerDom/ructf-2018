using System;
using System.Threading;
using System.Threading.Tasks;
using Hologram.Handlers;
using Hologram.Handlers.Schemas;
using Hologram.Http;
using Hologram.Ws;
using log4net;
using log4net.Config;

namespace Hologram
{
	internal static class Program
	{
		private static void Main()
		{
			XmlConfigurator.Configure();
			try
			{
				var coresAmount = Environment.ProcessorCount;
				ThreadPool.SetMinThreads(128 * coresAmount, 128 * coresAmount);
				var server = PrepareHttpServer();
				var wsServer = PrepareWsServer();
				
				Database.HologramsField.Init(
					Settings.HologramsPath, 
					(holo, s) => 
						wsServer.BroadcastAsync(HologramJsonSchema.FromHolo(holo), s, CancellationToken.None));
				
				Task.WhenAll(
					server.AcceptLoopAsync(CancellationToken.None),
					wsServer.AcceptLoopAsync(CancellationToken.None)
				).Wait();
			}
			catch (Exception ex)
			{
				Console.Error.WriteLine(ex);
				Log.Fatal("Unexpected exception", ex);
				Environment.Exit(ex.HResult == 0 ? ex.HResult : -1);
			}
		}

		private static HttpServer PrepareHttpServer()
		{
			var server = new HttpServer(int.Parse(Settings.HttpPort));
			return server
				.AddHandler(HologramsHandler.Instance);
		}

		private static WsServer PrepareWsServer()
		{
			var server = new WsServer(int.Parse(Settings.WsPort));
			return server;
		}

		private static readonly ILog Log = LogManager.GetLogger(typeof(Program));
	}
}

