using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using Hologram.Database.Loaders;
using Hologram.Models;
using log4net;

namespace Hologram.Database
{
    public static class HologramsField
    {
        private static ConcurrentDictionary<Guid, Holo> Holograms;
        private static Action<Holo, string> _listener;

        public static void Init(string path, Action<Holo, string> listener)
        {
            Holograms = new ConcurrentDictionary<Guid, Holo>();
            _listener = listener;

            var dumper = Dumper<Holo>
                .Create(path, DumpHologramsAsync)
                .ConfigureSleep(25);

            if (dumper.TryLoadSavedData(out var holograms))
            {
                foreach (var holo in holograms)
                    Holograms[holo.Id] = holo;
                Log.Info($"Successfully loaded {Holograms.Count} saved holograms!");
            }

            dumper.Start();
        }

        public static Guid AddHologram(Holo holo)
        {
            _listener(holo, null);
            Holograms[holo.Id] = holo;
            return holo.Id;
        }

        public static bool TryGetHologram(Guid id, out Holo hologram) => 
            Holograms.TryGetValue(id, out hologram);

        public static List<Holo> SearchHologramsAtPoint(Point point, int radius) => 
            Holograms.Select(x => x.Value).Where(x => x.Position.IsInSphere(point, radius)).ToList();

        private static Holo[] DumpHologramsAsync() => Holograms.Select(x => x.Value).ToArray();
        
        private static readonly ILog Log = LogManager.GetLogger(typeof(Program));
    }
}