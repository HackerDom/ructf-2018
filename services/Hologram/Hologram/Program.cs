using System;
using System.Threading;
using System.Threading.Tasks;
using Hologram.Database.Loaders;
using Hologram.Handlers;
using Hologram.Http;
using Hologram.Models;
using Hologram.Utils;
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
				var settings = SimpleSettings.Create("settings");


				var sleepPeriod = int.Parse(settings.GetValue("sleep"));
				var ttl = int.Parse(settings.GetValue("ttl"));
				Database.HologramField.Init(settings.GetValue("holograms"));

				var server = PrepareServer(settings);
				Task.WhenAll(server.AcceptLoopAsync(CancellationToken.None)).Wait();
			}
			catch (Exception ex)
			{
				Console.Error.WriteLine(ex);
				Log.Fatal("Unexpected exception", ex);
				Environment.Exit(ex.HResult == 0 ? ex.HResult : -1);
			}
		}

		private static HttpServer PrepareServer(SimpleSettings settings)
		{
			var port = int.Parse(settings.GetValue("port"));

			var server = new HttpServer(port);

			server
				.AddHandler(HologramsHandler.Instance);
//				.AddHandler(LoginHandler.Instance)
//				.AddHandler(AddPointHandler.Instance)
//				.AddHandler(GetAllPublicsHandler.Instance)
//				.AddHandler(GetPointsHandler.Instance)
//				.AddHandler(ShortestPathHandler.Instance);

			return server;
		}

		private static readonly ILog Log = LogManager.GetLogger(typeof(Program));
	}
}

