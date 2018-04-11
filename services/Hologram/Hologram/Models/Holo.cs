using System;

namespace Hologram.Models
{
    [Serializable]
    public class Holo
    {
        public Guid Id { get; }
        public Point Position { get; }
        public string Name { get; private set; }
        public string Body { get; private set; }

        public Holo(Point position)
        {
            Id = Guid.NewGuid();
            Position = position;
        }

        public Holo UpdateContent(string name, string body)
        {
            Name = name;
            Body = body;
            return this;
        }
    }
}