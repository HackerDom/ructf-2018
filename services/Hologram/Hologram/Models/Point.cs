using System;

namespace Hologram.Models
{
    [Serializable]
    public class Point
    {
        public int X { get; }
        public int Y { get; }
        public int Z { get; }

        public Point(int x, int y, int z)
        {
            X = x;
            Y = y;
            Z = z;
        }

        public Point((int x, int y, int z) cords): this(cords.x, cords.y, cords.z)
        {
        }

        public bool IsInSphere(Point sphereCenter, int sphereRadius) 
            => Math.Pow( X-sphereCenter.X, 2) 
               + Math.Pow(Y-sphereCenter.Y, 2)
               + Math.Pow(Z - sphereCenter.Z, 2) < Math.Pow(sphereRadius, 2);
    }
}