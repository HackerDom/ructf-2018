using System;
using System.Collections.Generic;
using System.IO;
using log4net;

namespace BulletinBoard.Utils
{
	public class SimpleSettings
	{
		private readonly string path;
		private readonly Dictionary<string, string> settings;

		public static SimpleSettings Create(string path)
		{
			try
			{
				path = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, path);

				var settings = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

				foreach (var line in File.ReadLines(path))
				{
					var cleanLine = line.CutEnd("#")?.Trim();
					if (string.IsNullOrEmpty(cleanLine))
						continue;


					var index = cleanLine.IndexOf("=", StringComparison.Ordinal);
					if (index < 0)
						settings[cleanLine] = null;
					else
					{
						var key = cleanLine.Substring(0, index).Trim();
						var value = cleanLine.Substring(index + 1).Trim();
						settings[key] = value;
					}
				}

				return new SimpleSettings(path, settings);
			}
			catch (Exception ex)
			{
				Log.Error($"can't process settings file {path}", ex);
				throw;
			}
		}

		public string GetValue(string key)
		{
			if (!settings.ContainsKey(key))
				throw new KeyNotFoundException($"settings file '{path}' doesn't contains key '{key}'");
			return settings[key];
		}

		private SimpleSettings(string path, Dictionary<string, string> settings)
		{
			this.path = path;
			this.settings = settings;
		}

		private static readonly ILog Log = LogManager.GetLogger(typeof(SimpleSettings));
	}
}