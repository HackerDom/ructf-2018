using System;
using System.Threading;
using System.Threading.Tasks;
using Hologram.Handlers;
using Hologram.Http;
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
				Database.HologramField.Init(Settings.HologramsPath);

				var server = PrepareServer();
				Task.WhenAll(server.AcceptLoopAsync(CancellationToken.None)).Wait();
			}
			catch (Exception ex)
			{
				Console.Error.WriteLine(ex);
				Log.Fatal("Unexpected exception", ex);
				Environment.Exit(ex.HResult == 0 ? ex.HResult : -1);
			}
		}

		private static HttpServer PrepareServer()
		{
			var server = new HttpServer(int.Parse(Settings.HttpPort));
			return server
				.AddHandler(HologramsHandler.Instance);
		}

		private static readonly ILog Log = LogManager.GetLogger(typeof(Program));
	}
}

