using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;

namespace Hologram.Handlers.Helpers
{
	public abstract class BaseHandler
	{
		public abstract Dictionary<HttpMethod, Func<HttpListenerContext, Task>> Methods { get; }
		public abstract string Path { get; }
	}
}