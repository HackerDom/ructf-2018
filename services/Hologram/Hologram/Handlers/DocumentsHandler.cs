using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Hologram.Handlers.Helpers;
using Hologram.Http;

namespace Hologram.Handlers
{
    public class DocumentsHandler: BaseHandler
    {
        public static readonly BaseHandler Instance = new DocumentsHandler();
        private const int searchRadiusLimit = 20;

        public override Dictionary<HttpMethod, Func<HttpListener, Task>> Methods { get; }
        public override string Path => "/api/documents";
        public override async Task Handle(HttpListenerContext context)
        {
            var query = context.Request.QueryList();
            if (!int.TryParse(query.Find(x => x.key == "rad").value, out var rad) || rad > searchRadiusLimit)
                throw new HttpException(400, $"Radius should be lower than {searchRadiusLimit}");
            await context.WriteStringAsync(string.Join(",", query))
                .ConfigureAwait(false);
        }
    }
}