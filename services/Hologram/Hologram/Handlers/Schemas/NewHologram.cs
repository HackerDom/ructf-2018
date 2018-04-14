using System;
using System.Runtime.Serialization;
using Hologram.Models;

namespace Hologram.Handlers.Schemas
{
    [DataContract(Namespace = "")]
    public class NewHologram
    {
        [DataMember(Name = "id")] public Guid Id;
        [DataMember(Name = "x", IsRequired = true)] public int X;
        [DataMember(Name = "y", IsRequired = true)] public int Y;
        [DataMember(Name = "z", IsRequired = true)] public int Z;

        [DataMember(Name = "name", IsRequired = true)] public string Name;
        [DataMember(Name = "body", IsRequired = true)] public string Body;
        
        public static NewHologram FromHolo(Holo hologram)
            => new NewHologram
            {
                X = hologram.Position.X,
                Y = hologram.Position.Y,
                Z = hologram.Position.Z,
                Id = hologram.Id,
                Name = hologram.Name,
                Body = hologram.Body
            };
    }
}