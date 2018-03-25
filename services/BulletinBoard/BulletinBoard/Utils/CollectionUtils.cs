using System.Collections.Concurrent;
using System.Collections.Generic;

namespace BulletinBoard.Utils
{
	public static class CollectionUtils
	{
		public static TValue GetOrDefault<TKey, TValue>(this IDictionary<TKey, TValue> dict, TKey key, TValue defaultValue = default(TValue)) where TKey : class
			=> key == null || dict == null ? defaultValue : dict.TryGetValue(key, out TValue value) ? value : defaultValue;

		public static void AddOrUpdateLocked<TKey, TValue>(this ConcurrentDictionary<TKey, HashSet<TValue>> dict, TKey key, TValue value)
		{
			dict?.AddOrUpdate(key, k => new HashSet<TValue> { value }, (k, set) =>
			{
				lock (set)
				{
					set.Add(value);
					return set;
				}
			});
		}

		public static List<TValue> GetClonedList<TKey, TValue>(this ConcurrentDictionary<TKey, HashSet<TValue>> dict, TKey key) where TKey : class 
		{
			var set = dict.GetOrDefault(key);
			if (set == null)
				return null;
			lock (set)
			{
				return new List<TValue>(set);
			}
		}

		public static bool IsNullOrEmpty<T>(this ICollection<T> collection)
			=> collection == null || collection.Count == 0;

		public static T PreLast<T>(this List<T> list) 
			=> list[list.Count - 2];
	}
}