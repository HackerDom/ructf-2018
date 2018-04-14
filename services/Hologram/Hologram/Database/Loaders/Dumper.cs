using System;
using System.Collections.Generic;
using System.IO;
using System.Runtime.Serialization;
using System.Runtime.Serialization.Formatters.Binary;
using System.Threading;
using log4net;

namespace Hologram.Database.Loaders
{
    public class Dumper<T>
    {
        private int secondsToSleep;
        private readonly string path;
        private readonly Func<IEnumerable<T>> objectsCollectionExtractor;
        private Thread worker;

        private Dumper(string path, Func<IEnumerable<T>> objectsCollectionExtractor)
        {
            secondsToSleep = 30;
            this.path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, path);
            this.objectsCollectionExtractor = objectsCollectionExtractor;
        }

        public Dumper<T> ConfigureSleep(int seconds)
        {
            secondsToSleep = seconds;
            return this;
        }

        public bool TryLoadSavedData(out IEnumerable<T> data)
        {
            data = Load(path);
            return !ReferenceEquals(data, null);
        }

        public void Start() 
            => new Thread(() => Save(path, secondsToSleep, objectsCollectionExtractor)).Start();

        public static Dumper<T> Create(string path, Func<IEnumerable<T>> func) => new Dumper<T>(path, func);

        private static void Save(string path, int sleep, Func<IEnumerable<T>> objectsCollectionGetter)
        {
            var formatter = new BinaryFormatter();
            while (true)
            {
                try
                {
                    using (var fs = new FileStream($"{path}.tmp", FileMode.Create, FileAccess.Write))
                    {
                        try 
                        {
                            formatter.Serialize(fs, objectsCollectionGetter());
                        }
                        catch (SerializationException e) 
                        {
                            Log.Warn($"Exception while saving file '{path}.tmp'", e);
                        }
                    }
                    if (File.Exists(path)) File.Delete(path);
                    File.Move($"{path}.tmp", path);
                }
                catch (Exception ex)
                {
                    Log.Warn($"Exception while saving file '{path}'", ex);
                }

                Thread.Sleep(sleep * 1000);
            }
        }

        private static IEnumerable<T> Load(string path)
        {
            try
            {
                using (var fs = new FileStream(path, FileMode.Open))
                    return (IEnumerable<T>) new BinaryFormatter().Deserialize(fs);
            }
            catch (FileNotFoundException e)
            {
                Log.Warn($"DB file doesn't exist!");
                return null;
            }
            catch (SerializationException e) 
            {
                Log.Warn($"Failed to deserialize. Reason: {e.Message}");
                return null;
            }
        }

        private static readonly ILog Log = LogManager.GetLogger(typeof(Dumper<T>));
    }
}