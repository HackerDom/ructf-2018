using System;
using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using Hologram.Database;
using Hologram.Handlers.Helpers;
using Hologram.Handlers.Schemas;
using Hologram.Http;
using Hologram.Models;
using Hologram.Utils;

namespace Hologram.Handlers
{
    public class HologramsHandler: BaseHandler
    {
        public static readonly BaseHandler Instance = new HologramsHandler();
        private const int searchRadiusLimit = 20;
        public override Dictionary<HttpMethod, Func<HttpListenerContext, Task>> Methods { get; }
        public override string Path => "/api/holograms";

        private HologramsHandler() => 
            Methods = new Dictionary<HttpMethod, Func<HttpListenerContext, Task>>
            {
                [HttpMethod.Get] = GetHologramAsync,
                [HttpMethod.Post] = PostHologramAsync,
                [HttpMethod.Put] = PutHologramLookuper
            };

        private async Task PutHologramLookuper(HttpListenerContext context) // todo logic + ws alternative
        {
            var query = context.Request.Query();
            if (!int.TryParse(query.Find(x => x.key == "rad").value, out var rad) || rad > searchRadiusLimit)
                throw new HttpException(400, $"Radius should be lower than {searchRadiusLimit}");
            await context.WriteStringAsync($"{string.Join(",", query)} and dict: {string.Join(",", query.ToDictionary(x => (x.key, x.value)))}")
                .ConfigureAwait(false);
        }

        private async Task PostHologramAsync(HttpListenerContext context)
        {
            var parsedHologram = await JsonHelper.TryParseJsonAsync<NewHologram>(context.Request.InputStream)
                .ConfigureAwait(false);
            
            if (parsedHologram is null)
                throw new HttpException(400, "Request should contain json object!");
            
            var newHologramId = HologramField.AddHologram(
                new Holo(new Point((parsedHologram.X, parsedHologram.Y, parsedHologram.Z)))
                    .UpdateContent(parsedHologram.Name, parsedHologram.Body));
            await context.Response.WriteObjectAsync(new Dictionary<string, Guid> {["id"] = newHologramId});
        }

        private async Task GetHologramAsync(HttpListenerContext context)
        {
            var query = context.Request.Query();
            if (!Guid.TryParse(query.Find(x => x.key == "id").value, out var guid))
                throw new HttpException(400, "Incorrect id has been sent!");

            if (!HologramField.TryGetHologram(guid, out var hologram))
                await context.Response.WriteObjectAsync(
                    new Dictionary<string, string> {["error"] = "no such id was found"});
            else
                await context.Response.WriteObjectAsync(NewHologram.FromHolo(hologram));
        }
    }
}