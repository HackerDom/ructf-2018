using System;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using Hologram.Utils;

namespace Hologram.Http
{
	public static class ResponseAsyncHelper
	{
		public static async Task WriteObjectAsync<T>(this HttpListenerResponse response, T obj)
		{
			var data = obj.ToJson();
			response.ContentType = ContentType;
			await response.WriteDataAsync(data).ConfigureAwait(false);
		}

		private static async Task WriteDataAsync(this HttpListenerResponse response, byte[] data)
		{
			await response.WriteDataAsync(data, 0, data?.Length ?? 0).ConfigureAwait(false);
		}

		private static async Task<int> WriteDataAsync(this HttpListenerResponse response, byte[] data, int offset, int count)
		{
			if(data == null || count == 0)
				response.ContentLength64 = 0;
			else
			{
				response.ContentLength64 = count;
				await response.OutputStream.WriteAsync(data, offset, count).ConfigureAwait(false);
			}
			return count;
		}

		public static async Task WriteStringAsync(this HttpListenerContext context, string value, Encoding encoding = null)
		{
			var buffer = value == null ? new byte[0] : (encoding ?? Encoding.UTF8).GetBytes(value);
			try
			{
				await
					context.Response.WriteDataAsync(buffer, 0, buffer.Length)
						.WithTimeout(HttpServerSettings.ReadWriteTimeout) //NOTE: HttpResponseStream is not cancellable with CancellationToken :(
						.ConfigureAwait(false);
			}
			catch(Exception e)
			{
				context.AbortConnection();
				throw new HttpConnectionClosed(e);
			}
		}

		public static void SetCookie(this HttpListenerContext context, string name, string value, bool httpOnly = false)
		{
			context.Response.Headers.Add(HttpResponseHeader.SetCookie, $"{name}={value}; path=/{(httpOnly ? "; HttpOnly" : null)}");
		}

		private const string ContentType = "application/json; charset=utf-8";
	}
}