using BulletinBoard.Http;
using BulletinBoard.Handlers.Helpers;

namespace BulletinBoard.Http
{
	internal static class HttpServerExtentions
	{
		public static HttpServer AddHandler(this HttpServer server, BaseHandler handler)
		{
			foreach (var method in handler.Methods)
				server.AddHandler(method.ToString(), handler.Path, handler.Handle);
			return server;
		}
	}
}