using System;
using System.Collections.Generic;
using System.Linq;

namespace Hologram.Utils
{
	public static class EnumerableExtentions
	{
		public static void ForEach<T>(this IEnumerable<T> enumerable, Action<T> action)
		{
			foreach (var item in enumerable)
				action(item);
		}

		public static IEnumerable<T> WhereNotNull<T>(this IEnumerable<T> enumerable) where T : class 
			=> enumerable.Where(item => item != null);

		public static IEnumerable<T> EmptyIfNull<T>(this IEnumerable<T> enumerable)
			=> enumerable ?? Enumerable.Empty<T>();

		public static Dictionary<TKey, TValue> ToDictionary<T, TKey, TValue>(
			this IEnumerable<T> enumerable, 
			Func<T, (TKey key, TValue value)> extractorFunc)
		{
			var result = new Dictionary<TKey, TValue>();
			foreach (var kvPair in enumerable.Select(extractorFunc))
				result[kvPair.key] = kvPair.value;
			return result;
		}
	}
}