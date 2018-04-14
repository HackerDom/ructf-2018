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
        public DateTime CreationDate { get; }

        public Holo(Point position)
        {
            Id = Guid.NewGuid();
            CreationDate = DateTime.Now;
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