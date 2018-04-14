using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using Hologram.Handlers.Schemas;
using Hologram.Models;
using Hologram.Utils;
using log4net;
using vtortola.WebSockets;
using vtortola.WebSockets.Rfc6455;

namespace Hologram.Ws
{
	internal class WsServer
	{
		public WsServer(int port)
		{
			var timeout = TimeSpan.FromSeconds(3);
			var readWriteTimeout = TimeSpan.FromSeconds(1);
			var options = new WebSocketListenerOptions
			{
				UseNagleAlgorithm = false,
				PingMode = PingModes.BandwidthSaving,
				PingTimeout = timeout,
				NegotiationTimeout = timeout,
				
				WebSocketSendTimeout = readWriteTimeout,
				WebSocketReceiveTimeout = readWriteTimeout,
				SubProtocols = new[] {"text"}
			};

			endpoint = new IPEndPoint(IPAddress.Any, port);
			listener = new WebSocketListener(endpoint, options);
			listener.Standards.RegisterStandard(new WebSocketFactoryRfc6455(listener));
		}

		public async Task AcceptLoopAsync(CancellationToken token)
		{
			token.Register(() =>
			{
				listener.Dispose();
				Log.Error("WebSocketServer stopped");
			});

			listener.Start();
			Log.Info($"WebSocketServer started at '{endpoint}'");
			while(!token.IsCancellationRequested)
			{
				try
				{
					var ws = await listener.AcceptWebSocketAsync(token).ConfigureAwait(false);
					if (ws == null)
						continue;
#pragma warning disable CS4014 
					Task.Run(() => TryRegister(ws, token), token);
#pragma warning restore CS4014
				} catch {}
			}
		}

		public Task BroadcastAsync(HologramJsonSchema holo, string msg, CancellationToken token)
		{
			if (msg == null)
				msg = holo.ToJsonString();
			return
				Task.WhenAll(
					sockets
						.Where(pair =>
						{
							var ws = pair.Key;
							if(ws.IsConnected)
								return true;
							Remove(ws);
							return false;
						})
						.Select(pair => TrySendAsync(pair.Key, pair.Value, holo, token, msg)));
		}

		private async Task TryRegister(WebSocket ws, CancellationToken token)
		{
			try
			{
				Log.Info($"Processing request for {ws.HttpRequest.Path()}...");
				var connection = CreateConnection(ws);
				if (!connection.HasValue) { 
					ws.Close();
					return;
				}
				var conn = connection.Value;
				sockets[ws] = conn;
				Log.Info($"Request for {ws.HttpRequest.Path()} has been registered!");
				await Task.WhenAll(conn.InitData.Invoke().Select(holo => TrySendAsync(ws, conn, holo, token))).ConfigureAwait(false);
				Log.Info("Initial data has been sent!");
			}
			catch
			{
				ws.Dispose();
			}
		}

		private async Task TrySendAsync(WebSocket ws, Connection connection, HologramJsonSchema hologram, CancellationToken token, string msg = null)
		{
			try
			{
				if (!connection.NeedSend(hologram))
					return;
				msg = msg ?? hologram.ToJsonString();
				using(await connection.Lock.AcquireAsync(token).ConfigureAwait(false))
					await ws.WriteStringAsync(msg, token).ConfigureAwait(false);
			}
			catch
			{
				Remove(ws);
			}
		}

		private void Remove(WebSocket ws)
		{
			if (!sockets.TryRemove(ws, out var state))
				return;
			state.Lock.Dispose();
			ws.Dispose();
		}

		private struct Connection
		{
			public Predicate<HologramJsonSchema> NeedSend;
			public AsyncLockSource Lock;
			public Func<IEnumerable<HologramJsonSchema>> InitData;
		}

		private static Connection? CreateConnection(WebSocket ws)
		{
			try
			{	
				if (ws.HttpRequest.Path() == "/ws/holograms")
				{
					var query = ws.HttpRequest.Query();
					if (!int.TryParse(query.Find(x => x.key == "rad").value, out var rad) || rad > 20)
						return null;
					return new Connection
					{
						NeedSend =
							hologram => IsHologramInRadius(hologram, query.ToDictionary(x => (x.key, x.value))),
						Lock =
							new AsyncLockSource(),
						InitData =
							() => SearchHolograms(query.ToDictionary(x => (x.key, x.value)))
					};
				}
			}
			catch (Exception e)
			{
				Log.Warn($"Unknown exception: {e.Message}, \n {e.StackTrace}");
			}
			return null;
		}

		private static List<HologramJsonSchema> SearchHolograms(Dictionary<string, string> config)
		{
			if (int.TryParse(config["rad"], out var rad) &
				Point.TryParse(config["x"], config["y"], config["z"], out var point)
			)
				return Database.HologramsField
					.SearchHologramsAtPoint(point, rad)
					.OrderByDescending(x => x.CreationDate).Take(100)
					.Select(HologramJsonSchema.FromHolo).ToList();
			return null;
		}

		private static bool IsHologramInRadius(HologramJsonSchema holo, Dictionary<string, string> config)
		{
			int.TryParse(config["rad"], out var rad);
			Point.TryParse(config["x"], config["y"], config["z"], out var point);
			return new Point(holo.X, holo.Y, holo.Z).IsInSphere(point, rad);
		}

		private readonly ConcurrentDictionary<WebSocket, Connection> sockets = new ConcurrentDictionary<WebSocket, Connection>();
		private readonly WebSocketListener listener;
		private readonly IPEndPoint endpoint;

		private static readonly ILog Log = LogManager.GetLogger(typeof(WsServer));
	}
}