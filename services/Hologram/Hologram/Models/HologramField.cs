using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Linq;

namespace Hologram.Models
{
    public static class HologramField
    {
        private static ConcurrentDictionary<Guid, Hologram> Holograms;

        public static void AddHologram(Hologram hologram) => Holograms[hologram.Id] = hologram;

        public static Hologram GetHologram(Guid id) => Holograms.TryGetValue(id, out var hologram) ? hologram : null;

        public static List<Hologram> SearchHologramsAtPoint(Point point, int radius) => 
            Holograms.Select(x => x.Value).Where(x => x.Position.IsInSphere(point, radius)).ToList();

        public static Hologram[] DumpHologramsAsync() => Holograms.Select(x => x.Value).ToArray();
    }
}