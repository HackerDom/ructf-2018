using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Http;
using System.Reflection;
using System.Threading.Tasks;

namespace Hologram.Handlers.Helpers
{
	public abstract class BaseHandler
	{
		public abstract Dictionary<HttpMethod, Func<HttpListener, Task>> Methods { get; }
		public abstract string Path { get; }

		public abstract Task Handle(HttpListenerContext context);

		protected BaseHandler()
		{
			//GetType().GetMethods().Where(x => x.GetCustomAttribute<MethodAttribute>())
		}
	}
}