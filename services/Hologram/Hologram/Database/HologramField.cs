using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;
using Hologram.Models;

namespace Hologram.Database
{
    public static class HologramField
    {
        private static ConcurrentDictionary<Guid, Holo> Holograms;

        public static void Init(IEnumerable<Holo> holograms=null)
        {
            Holograms = new ConcurrentDictionary<Guid, Holo>();
            if (holograms is null) return;
            foreach (var hologram in holograms)
                Holograms[hologram.Id] = hologram;
        }

        public static Guid AddHologram(Holo holo)
        {
            Holograms[holo.Id] = holo;
            return holo.Id;
        }

        public static bool TryGetHologram(Guid id, out Holo hologram) => 
            Holograms.TryGetValue(id, out hologram);

        public static List<Holo> SearchHologramsAtPoint(Point point, int radius) => 
            Holograms.Select(x => x.Value).Where(x => x.Position.IsInSphere(point, radius)).ToList();

        public static Holo[] DumpHologramsAsync() => Holograms.Select(x => x.Value).ToArray();
    }
}