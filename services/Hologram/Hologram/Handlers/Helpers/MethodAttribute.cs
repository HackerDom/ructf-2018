using System;
using System.Net.Http;

namespace Hologram.Handlers.Helpers
{
    public class MethodAttribute: Attribute
    {
        public HttpMethod Method { get; }
        public MethodAttribute(HttpMethod method) => Method = method;
    }
}