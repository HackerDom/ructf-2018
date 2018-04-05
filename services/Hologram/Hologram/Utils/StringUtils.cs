using System;

namespace Hologram.Utils
{
	public static class StringUtils
	{
		public static string CutEnd(this string str, string delim)
		{
			if (str == null || delim == null)
				return null;
			var index = str.IndexOf(delim, StringComparison.OrdinalIgnoreCase);
			return index < 0 ? str : str.Substring(0, index);
		}

		public static bool IsSignificant(this string str)
		{
			return !string.IsNullOrEmpty(str);
		}

		public static bool AllSymbolsAsciiPrinted(this string str)
		{
			// ReSharper disable once LoopCanBeConvertedToQuery
			// ReSharper disable once ForCanBeConvertedToForeach
			for (var i = 0; i < str.Length; ++i)
				if (str[i] <= ' ' || str[i] > '~')
					return false;
			return true;
		}
	}
}