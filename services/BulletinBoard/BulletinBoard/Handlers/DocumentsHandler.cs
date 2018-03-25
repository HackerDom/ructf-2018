using System.Collections.Generic;
using System.Net;
using System.Net.Http;
using System.Threading.Tasks;
using BulletinBoard.Handlers.Helpers;
using BulletinBoard.Http;


namespace BulletinBoard.Handlers
{
    public class DocumentsHandler: BaseHandler
    {
        public static readonly BaseHandler Instance = new DocumentsHandler();

        private const int searchRadiusLimit = 20;
        public override IEnumerable<HttpMethod> Methods => new[] {HttpMethod.Get};
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