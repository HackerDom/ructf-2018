using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;

namespace Hologram.Http
{
    public static class HttpListenerRequestExtentions
    {
        internal static List<(string key, string value)> Query(this HttpListenerRequest request) 
            => request.Url.Query.Substring(1)
                .Split(new [] {'&'}, StringSplitOptions.RemoveEmptyEntries)
                .Select(x => x.Split(new [] {'='}, StringSplitOptions.RemoveEmptyEntries))
                .Select(x => x.Length == 2 ? CreateDecodedItem(x[0], x[1]): CreateDecodedItem(x[0]))
                .ToList();

        private static (string key, string value) CreateDecodedItem(string key, string value="") 
            => (WebUtility.HtmlDecode(key), WebUtility.HtmlDecode(value));
    }
}