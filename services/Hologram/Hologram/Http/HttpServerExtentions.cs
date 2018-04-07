using Hologram.Handlers.Helpers;

namespace Hologram.Http
{
	internal static class HttpServerExtentions
	{
		public static HttpServer AddHandler(this HttpServer server, BaseHandler handler)
		{
			foreach (var method in handler.Methods)
				server.AddHandler(method.Key.ToString(), handler.Path, method.Value);
			return server;
		}
	}
}