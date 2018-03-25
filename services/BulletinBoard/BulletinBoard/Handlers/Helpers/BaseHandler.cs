using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;


namespace BulletinBoard.Handlers.Helpers
{
	public abstract class BaseHandler
	{
		public abstract IEnumerable<HttpMethod> Methods { get; }
		public abstract string Path { get; }

		public abstract Task Handle(HttpListenerContext context);
	}
}