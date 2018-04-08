using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Hologram.Handlers.Helpers;
using Hologram.Http;
using Hologram.Utils;

namespace Hologram.Handlers
{
    public class DocumentsHandler: BaseHandler
    {
        public static readonly BaseHandler Instance = new DocumentsHandler();
        private const int searchRadiusLimit = 20;
        public override Dictionary<HttpMethod, Func<HttpListenerContext, Task>> Methods { get; }
        public override string Path => "/api/holograms";

        private DocumentsHandler() => 
            Methods = new Dictionary<HttpMethod, Func<HttpListenerContext, Task>>
            {
                [HttpMethod.Get] = LookupForHolograms
            };

        private async Task LookupForHolograms(HttpListenerContext context)
        {
            var query = context.Request.QueryList();
            if (!int.TryParse(query.Find(x => x.key == "rad").value, out var rad) || rad > searchRadiusLimit)
                throw new HttpException(400, $"Radius should be lower than {searchRadiusLimit}");
            await context.WriteStringAsync($"{string.Join(",", query)} and dict: {string.Join(",", query.ToDictionary(x => (x.key, x.value)))}")
                .ConfigureAwait(false);
        }
    }
}