using System.Configuration;

namespace Hologram
{
    public static class Settings
    {
        public static string HologramsPath => ConfigurationManager.AppSettings["hologramsPath"];
        public static string HttpPort => ConfigurationManager.AppSettings["httpPort"];
        public static string WsPort => ConfigurationManager.AppSettings["wsPort"];
    }
}