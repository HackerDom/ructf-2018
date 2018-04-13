using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using vtortola.WebSockets;

namespace Hologram.Ws
{
    public static class WsServerExtentions
    {
        internal static List<(string key, string value)> Query(this WebSocketHttpRequest request)
        {
            if (!request.RequestUri.ToString().Contains("?"))
                return new List<(string key, string value)>();
            if (request.RequestUri.ToString().Count(x => x == '?') > 1)
                throw new Exception("Unexpected query string symbols!");
            return request.RequestUri.ToString().Split(new[] {'?'}, StringSplitOptions.RemoveEmptyEntries)[1]
                .Split(new[] {'&'}, StringSplitOptions.RemoveEmptyEntries)
                .Select(x => x.Split(new[] {'='}, StringSplitOptions.RemoveEmptyEntries))
                .Select(x => x.Length == 2 ? CreateDecodedItem(x[0], x[1]) : CreateDecodedItem(x[0]))
                .ToList();
        }

        internal static string Path(this WebSocketHttpRequest request) => 
            !request.RequestUri.ToString().Contains("?")
                ? request.RequestUri.ToString() 
                : request.RequestUri.ToString()
                    .Split(new[] {'?'}, StringSplitOptions.RemoveEmptyEntries)
                    .First().TrimEnd('/', '\\');

        private static (string key, string value) CreateDecodedItem(string key, string value="") 
            => (WebUtility.HtmlDecode(key), WebUtility.HtmlDecode(value));
    }
}