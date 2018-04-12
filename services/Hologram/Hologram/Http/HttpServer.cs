using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Net;
using System.Threading;
using System.Threading.Tasks;
using log4net;

namespace Hologram.Http
{
	internal class HttpServer
	{
		public HttpServer(int port)
		{
			listener = new HttpListener {IgnoreWriteExceptions = true};
			listener.Prefixes.Add($"http://*:{port}/");
		}

		public HttpServer AddHandler(string method, string path, Func<HttpListenerContext, Task> callback)
		{
			if(listener.IsListening)
				throw new InvalidOperationException("Can't add handler after listening started");
			path = path.TrimEnd('/');
			var handler = new Handler {Path = path, Method = method, Callback = callback};
			if (!handlers.ContainsKey(path))
				handlers[path] = new Dictionary<string, Handler>();
			handlers[path][method] = handler;
			return this;
		}

		public async Task AcceptLoopAsync(CancellationToken token)
		{
			token.Register(() =>
			{
				listener.Stop();
				Log.Info("HttpServer stopped");
			});

			listener.Start();
			Log.Info($"HttpServer started at '{string.Join(";", listener.Prefixes)}'");
			while(!token.IsCancellationRequested)
			{
				try
				{
					var context = await listener.GetContextAsync().ConfigureAwait(false);
					//Console.WriteLine($"[{context.Request.RemoteEndPoint}] {context.Request.HttpMethod} {context.Request.Url.PathAndQuery}");
#pragma warning disable CS4014 // Because this call is not awaited, execution of the current method continues before the call is completed
					Task.Run(() => TryProcessRequestAsync(context), token);
#pragma warning restore CS4014 // Because this call is not awaited, execution of the current method continues before the call is completed
				}
				catch(Exception e)
				{
					if(!token.IsCancellationRequested)
						Log.Error(e);
				}
			}
		}

		private async void TryProcessRequestAsync(HttpListenerContext context)
		{
			Log.Info($"Request start {context.Request.Url.LocalPath}");
			var status = -1;
			var sw = Stopwatch.StartNew();
			try
			{
				var response = context.Response;
				response.Headers["Server"] = HttpServerSettings.ServerName;
				//NOTE: Mono breaks keep-alive connection on disponsing HttpResponse
				//using(var response = context.Response)
				try
				{
					await ProcessRequestAsync(context).ConfigureAwait(false);
				}
				catch(HttpConnectionClosed) {}
				catch(Exception e)
				{
					Log.Error(e);
					var httpException = e as HttpException;
					response.StatusCode = httpException?.Status ?? 500;
					response.ContentType = "text/plain; charset=utf-8";
					await context.WriteStringAsync(httpException?.Message ?? "Internal Server Error")
						.ConfigureAwait(false);
				}
				finally
				{
					status = response.StatusCode;
					response.Close();
				}
			}
			catch(Exception e)
			{
				if(!(e is InvalidOperationException))
					Log.Error(e);
			}
			Log.Info($"Request end {context.Request.Url.LocalPath} with status {status}, elapsed {sw.Elapsed}");
		}

		private async Task ProcessRequestAsync(HttpListenerContext context)
		{
			var possibleUrlHandlers = FindPossibleUrlHandlers(context.Request.Url.LocalPath);
			if(ReferenceEquals(possibleUrlHandlers, null))
				throw new HttpException(404, "Not Found");
			
			if(!possibleUrlHandlers.ContainsKey(context.Request.HttpMethod))
				throw new HttpException(405, "Method Not Allowed");

			if(context.Request.HasEntityBody)
			{
				if(context.Request.ContentLength64 < 0)
					throw new HttpException(411, "Length Required");

				if(context.Request.ContentLength64 > HttpServerSettings.MaxRequestSize)
					throw new HttpException(413, "Request Entity Too Large");
			}

			await possibleUrlHandlers[context.Request.HttpMethod].Callback(context).ConfigureAwait(false);
		}

		private Dictionary<string, Handler> FindPossibleUrlHandlers(string path)
		{
			path = path.TrimEnd('/');
			return handlers.ContainsKey(path) ? handlers[path] : null;
		}

		private class Handler
		{
			public string Path;
			public string Method;
			public Func<HttpListenerContext, Task> Callback;
		}

		private readonly Dictionary<string, Dictionary<string, Handler>> handlers
			= new Dictionary<string, Dictionary<string, Handler>>();
		private readonly HttpListener listener;

		private static readonly ILog Log = LogManager.GetLogger(typeof(HttpServer));
	}

	public class HttpException : Exception
	{
		public HttpException(int status, string message): base(message) => Status = status;
		public int Status { get; }
	}

	public class HttpConnectionClosed : Exception
	{
		public HttpConnectionClosed(Exception innerException)
			: base(null, innerException)
		{
		}
	}
}