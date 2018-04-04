using System;
using System.Net;
using Hologram.Utils;

namespace Hologram.Http
{
	internal static class HttpContextHelper
	{
		static HttpContextHelper()
		{
			if(!RuntimeHelper.IsMono)
				Abort = ReflectionUtils.GetMethodInvoker<HttpListenerContext>("Abort");
			else
			{
				var method = ReflectionUtils.GetFieldMethodInvoker<HttpListenerContext, object>("cnc", "OnTimeout");
				Abort = ctx => method(ctx, null);
			}
		}

		public static void AbortConnection(this HttpListenerContext context)
		{
			try
			{
				Abort(context);
			}
			catch
			{
				// ignored
			}
		}

		private static readonly Action<HttpListenerContext> Abort;
	}
}