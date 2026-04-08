"""
leetcode_api.py — Full problem bank + real LeetCode GraphQL verification
"""
import random
import cloudscraper
import requests

PROBLEMS = {
    "dsa": {
        "Easy": [
            {
                "id": "1", "title": "Two Sum", "slug": "two-sum", "difficulty": "Easy", "topic": "Array, Hash Map",
                "description": "Given an array of integers <code>nums</code> and an integer <code>target</code>, return <em>indices of the two numbers that add up to target</em>.<br><br><strong>Example:</strong><br><code>Input: nums=[2,7,11,15], target=9</code><br><code>Output: [0,1]</code><br><br><strong>Constraints:</strong><br>• 2 ≤ nums.length ≤ 10⁴<br>• -10⁹ ≤ nums[i] ≤ 10⁹",
                "hints": ["Use a hash map to store numbers seen so far.", "For each num, check if (target - num) exists in the map.", "Store the index alongside each number."],
                "test_cases": [{"input": "nums=[2,7,11,15], target=9", "expected": "[0,1]"}, {"input": "nums=[3,2,4], target=6", "expected": "[1,2]"}, {"input": "nums=[3,3], target=6", "expected": "[0,1]"}],
                "solutions": {
                    "python": "def twoSum(nums, target):\n    seen = {}\n    for i, num in enumerate(nums):\n        complement = target - num\n        if complement in seen:\n            return [seen[complement], i]\n        seen[num] = i\n    return []\n\nprint(twoSum([2,7,11,15], 9))  # [0,1]",
                    "javascript": "function twoSum(nums, target) {\n    const seen = new Map();\n    for (let i = 0; i < nums.length; i++) {\n        const comp = target - nums[i];\n        if (seen.has(comp)) return [seen.get(comp), i];\n        seen.set(nums[i], i);\n    }\n    return [];\n}\nconsole.log(twoSum([2,7,11,15], 9)); // [0,1]",
                    "java": "import java.util.HashMap;\nclass Solution {\n    public int[] twoSum(int[] nums, int target) {\n        HashMap<Integer,Integer> map = new HashMap<>();\n        for (int i=0;i<nums.length;i++) {\n            int comp = target - nums[i];\n            if (map.containsKey(comp)) return new int[]{map.get(comp),i};\n            map.put(nums[i],i);\n        }\n        return new int[]{};\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
            {
                "id": "704", "title": "Binary Search", "slug": "binary-search", "difficulty": "Easy", "topic": "Array, Binary Search",
                "description": "Given a sorted array <code>nums</code> and integer <code>target</code>, return the index of target or -1 if not found.<br><br><strong>Example:</strong><br><code>Input: nums=[-1,0,3,5,9,12], target=9</code><br><code>Output: 4</code>",
                "hints": ["Use two pointers: left=0, right=len-1.", "mid=(left+right)//2 each loop.", "If nums[mid] < target, search right half. Otherwise left half."],
                "test_cases": [{"input": "nums=[-1,0,3,5,9,12], target=9", "expected": "4"}, {"input": "nums=[-1,0,3,5,9,12], target=2", "expected": "-1"}],
                "solutions": {
                    "python": "def search(nums, target):\n    left, right = 0, len(nums)-1\n    while left <= right:\n        mid = (left+right)//2\n        if nums[mid] == target: return mid\n        elif nums[mid] < target: left = mid+1\n        else: right = mid-1\n    return -1\n\nprint(search([-1,0,3,5,9,12],9))  # 4",
                    "javascript": "function search(nums, target) {\n    let left=0, right=nums.length-1;\n    while (left<=right) {\n        const mid = Math.floor((left+right)/2);\n        if (nums[mid]===target) return mid;\n        else if (nums[mid]<target) left=mid+1;\n        else right=mid-1;\n    }\n    return -1;\n}",
                    "java": "class Solution {\n    public int search(int[] nums, int target) {\n        int left=0,right=nums.length-1;\n        while(left<=right){\n            int mid=left+(right-left)/2;\n            if(nums[mid]==target) return mid;\n            else if(nums[mid]<target) left=mid+1;\n            else right=mid-1;\n        }\n        return -1;\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
            {
                "id": "206", "title": "Reverse Linked List", "slug": "reverse-linked-list", "difficulty": "Easy", "topic": "Linked List",
                "description": "Given the <code>head</code> of a singly linked list, reverse it and return the reversed list.<br><br><strong>Example:</strong><br><code>Input: [1,2,3,4,5]</code><br><code>Output: [5,4,3,2,1]</code>",
                "hints": ["Use three pointers: prev=None, curr=head, next.", "Reverse: curr.next = prev, then advance all three.", "Return prev at the end."],
                "test_cases": [{"input": "head=[1,2,3,4,5]", "expected": "[5,4,3,2,1]"}, {"input": "head=[1,2]", "expected": "[2,1]"}],
                "solutions": {
                    "python": "def reverseList(head):\n    prev = None\n    curr = head\n    while curr:\n        next_node = curr.next\n        curr.next = prev\n        prev = curr\n        curr = next_node\n    return prev",
                    "javascript": "function reverseList(head) {\n    let prev=null, curr=head;\n    while (curr) {\n        const next=curr.next;\n        curr.next=prev;\n        prev=curr;\n        curr=next;\n    }\n    return prev;\n}",
                    "java": "class Solution {\n    public ListNode reverseList(ListNode head) {\n        ListNode prev=null,curr=head;\n        while(curr!=null){\n            ListNode next=curr.next;\n            curr.next=prev;\n            prev=curr;\n            curr=next;\n        }\n        return prev;\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
            {
                "id": "121", "title": "Best Time to Buy and Sell Stock", "slug": "best-time-to-buy-and-sell-stock", "difficulty": "Easy", "topic": "Array, Greedy",
                "description": "Given <code>prices[i]</code> = price on day i, find the max profit from one buy then sell. Return 0 if no profit.<br><br><strong>Example:</strong><br><code>Input: [7,1,5,3,6,4]</code><br><code>Output: 5</code> (buy at 1, sell at 6)",
                "hints": ["Track the minimum price seen so far.", "At each day, profit = price - min_price.", "Track the maximum profit across all days."],
                "test_cases": [{"input": "prices=[7,1,5,3,6,4]", "expected": "5"}, {"input": "prices=[7,6,4,3,1]", "expected": "0"}],
                "solutions": {
                    "python": "def maxProfit(prices):\n    min_p = float('inf')\n    max_profit = 0\n    for p in prices:\n        min_p = min(min_p, p)\n        max_profit = max(max_profit, p - min_p)\n    return max_profit",
                    "javascript": "function maxProfit(prices) {\n    let minP=Infinity, maxPr=0;\n    for (const p of prices) {\n        minP = Math.min(minP, p);\n        maxPr = Math.max(maxPr, p - minP);\n    }\n    return maxPr;\n}",
                    "java": "class Solution {\n    public int maxProfit(int[] prices) {\n        int minP=Integer.MAX_VALUE, maxPr=0;\n        for (int p:prices) {\n            minP=Math.min(minP,p);\n            maxPr=Math.max(maxPr,p-minP);\n        }\n        return maxPr;\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
            {
                "id": "20", "title": "Valid Parentheses", "slug": "valid-parentheses", "difficulty": "Easy", "topic": "Stack, String",
                "description": "Given a string <code>s</code> of brackets <code>()[]{}</code>, determine if the brackets are valid (opened and closed in correct order).<br><br><strong>Example:</strong><br><code>Input: \"()[]{}\"</code><br><code>Output: true</code>",
                "hints": ["Use a stack.", "Push opening brackets. On closing bracket, check the top.", "At end, stack must be empty."],
                "test_cases": [{"input": 's="()[]{}"', "expected": "true"}, {"input": 's="(]"', "expected": "false"}, {"input": 's="([)]"', "expected": "false"}],
                "solutions": {
                    "python": "def isValid(s):\n    stack = []\n    pairs = {')':'(', ']':'[', '}':'{'}\n    for c in s:\n        if c in '([{':\n            stack.append(c)\n        elif not stack or stack[-1] != pairs[c]:\n            return False\n        else:\n            stack.pop()\n    return not stack",
                    "javascript": "function isValid(s) {\n    const stack=[], pairs={')':'(', ']':'[', '}':'{'};\n    for (const c of s) {\n        if ('([{'.includes(c)) stack.push(c);\n        else if (!stack.length || stack[stack.length-1]!==pairs[c]) return false;\n        else stack.pop();\n    }\n    return stack.length===0;\n}",
                    "java": "class Solution {\n    public boolean isValid(String s) {\n        Deque<Character> stack=new ArrayDeque<>();\n        for (char c:s.toCharArray()) {\n            if (c=='('||c=='['||c=='{') stack.push(c);\n            else if (stack.isEmpty()) return false;\n            else if (c==')'&&stack.peek()!='(') return false;\n            else if (c==']'&&stack.peek()!='[') return false;\n            else if (c=='}'&&stack.peek()!='{') return false;\n            else stack.pop();\n        }\n        return stack.isEmpty();\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
        ],
        "Medium": [
            {
                "id": "3", "title": "Longest Substring Without Repeating Characters", "slug": "longest-substring-without-repeating-characters", "difficulty": "Medium", "topic": "String, Sliding Window",
                "description": "Given a string <code>s</code>, find the length of the <strong>longest substring</strong> without repeating characters.<br><br><strong>Example:</strong><br><code>Input: s=\"abcabcbb\"</code><br><code>Output: 3</code> (substring \"abc\")",
                "hints": ["Use sliding window with two pointers (left, right).", "Keep a set of chars in the current window.", "When a duplicate is found, shrink from the left."],
                "test_cases": [{"input": 's="abcabcbb"', "expected": "3"}, {"input": 's="bbbbb"', "expected": "1"}, {"input": 's="pwwkew"', "expected": "3"}],
                "solutions": {
                    "python": "def lengthOfLongestSubstring(s):\n    seen = set()\n    left = max_len = 0\n    for right in range(len(s)):\n        while s[right] in seen:\n            seen.remove(s[left])\n            left += 1\n        seen.add(s[right])\n        max_len = max(max_len, right-left+1)\n    return max_len\n\nprint(lengthOfLongestSubstring('abcabcbb'))  # 3",
                    "javascript": "function lengthOfLongestSubstring(s) {\n    const set = new Set();\n    let left=0, max=0;\n    for (let right=0;right<s.length;right++) {\n        while (set.has(s[right])) set.delete(s[left++]);\n        set.add(s[right]);\n        max = Math.max(max, right-left+1);\n    }\n    return max;\n}",
                    "java": "class Solution {\n    public int lengthOfLongestSubstring(String s) {\n        Set<Character> set=new HashSet<>();\n        int left=0,max=0;\n        for(int r=0;r<s.length();r++){\n            while(set.contains(s.charAt(r))) set.remove(s.charAt(left++));\n            set.add(s.charAt(r));\n            max=Math.max(max,r-left+1);\n        }\n        return max;\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
            {
                "id": "200", "title": "Number of Islands", "slug": "number-of-islands", "difficulty": "Medium", "topic": "DFS, BFS, Grid",
                "description": "Given an m×n binary grid where '1' is land and '0' is water, count the number of islands.<br><br><strong>Example:</strong><br><code>Input: [[\"1\",\"1\",\"0\"],[\"1\",\"1\",\"0\"],[\"0\",\"0\",\"1\"]]</code><br><code>Output: 2</code>",
                "hints": ["DFS: when you find a '1', increment count and DFS to sink it.", "Mark visited cells by changing '1' to '0'.", "Explore all 4 directions from each cell."],
                "test_cases": [{"input": '[[\"1\",\"1\",\"0\"],[\"1\",\"1\",\"0\"],[\"0\",\"0\",\"1\"]]', "expected": "2"}],
                "solutions": {
                    "python": "def numIslands(grid):\n    count = 0\n    def dfs(r,c):\n        if r<0 or r>=len(grid) or c<0 or c>=len(grid[0]) or grid[r][c]=='0': return\n        grid[r][c]='0'\n        dfs(r+1,c);dfs(r-1,c);dfs(r,c+1);dfs(r,c-1)\n    for r in range(len(grid)):\n        for c in range(len(grid[0])):\n            if grid[r][c]=='1': dfs(r,c); count+=1\n    return count",
                    "javascript": "function numIslands(grid) {\n    let count=0;\n    const dfs=(r,c)=>{\n        if(r<0||r>=grid.length||c<0||c>=grid[0].length||grid[r][c]==='0') return;\n        grid[r][c]='0';\n        dfs(r+1,c);dfs(r-1,c);dfs(r,c+1);dfs(r,c-1);\n    };\n    for(let r=0;r<grid.length;r++)\n        for(let c=0;c<grid[0].length;c++)\n            if(grid[r][c]==='1'){dfs(r,c);count++;}\n    return count;\n}",
                    "java": "class Solution {\n    public int numIslands(char[][] g){\n        int count=0;\n        for(int r=0;r<g.length;r++)\n            for(int c=0;c<g[0].length;c++)\n                if(g[r][c]=='1'){dfs(g,r,c);count++;}\n        return count;\n    }\n    void dfs(char[][] g,int r,int c){\n        if(r<0||r>=g.length||c<0||c>=g[0].length||g[r][c]=='0') return;\n        g[r][c]='0';\n        dfs(g,r+1,c);dfs(g,r-1,c);dfs(g,r,c+1);dfs(g,r,c-1);\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
            {
                "id": "15", "title": "3Sum", "slug": "3sum", "difficulty": "Medium", "topic": "Array, Two Pointers, Sorting",
                "description": "Given array <code>nums</code>, return all unique triplets that sum to 0.<br><br><strong>Example:</strong><br><code>Input: [-1,0,1,2,-1,-4]</code><br><code>Output: [[-1,-1,2],[-1,0,1]]</code>",
                "hints": ["Sort the array first.", "Fix one number, use two pointers on the rest.", "Skip duplicates carefully."],
                "test_cases": [{"input": "nums=[-1,0,1,2,-1,-4]", "expected": "[[-1,-1,2],[-1,0,1]]"}, {"input": "nums=[0,0,0]", "expected": "[[0,0,0]]"}],
                "solutions": {
                    "python": "def threeSum(nums):\n    nums.sort()\n    res = []\n    for i in range(len(nums)-2):\n        if i>0 and nums[i]==nums[i-1]: continue\n        l,r = i+1, len(nums)-1\n        while l<r:\n            s = nums[i]+nums[l]+nums[r]\n            if s==0: res.append([nums[i],nums[l],nums[r]]); l+=1; r-=1\n            elif s<0: l+=1\n            else: r-=1\n    return res",
                    "javascript": "function threeSum(nums) {\n    nums.sort((a,b)=>a-b);\n    const res=[];\n    for(let i=0;i<nums.length-2;i++){\n        if(i>0&&nums[i]===nums[i-1]) continue;\n        let l=i+1,r=nums.length-1;\n        while(l<r){\n            const s=nums[i]+nums[l]+nums[r];\n            if(s===0){res.push([nums[i],nums[l],nums[r]]);l++;r--;}\n            else if(s<0)l++; else r--;\n        }\n    }\n    return res;\n}",
                    "java": "class Solution {\n    public List<List<Integer>> threeSum(int[] nums) {\n        Arrays.sort(nums);\n        List<List<Integer>> res=new ArrayList<>();\n        for(int i=0;i<nums.length-2;i++){\n            if(i>0&&nums[i]==nums[i-1]) continue;\n            int l=i+1,r=nums.length-1;\n            while(l<r){\n                int s=nums[i]+nums[l]+nums[r];\n                if(s==0){res.add(Arrays.asList(nums[i],nums[l],nums[r]));l++;r--;}\n                else if(s<0)l++; else r--;\n            }\n        }\n        return res;\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
        ],
        "Hard": [
            {
                "id": "42", "title": "Trapping Rain Water", "slug": "trapping-rain-water", "difficulty": "Hard", "topic": "Array, Two Pointers",
                "description": "Given n non-negative integers representing elevation heights, compute how much water it can trap.<br><br><strong>Example:</strong><br><code>Input: [0,1,0,2,1,0,1,3,2,1,2,1]</code><br><code>Output: 6</code>",
                "hints": ["Water at each pos = min(max_left, max_right) - height[i].", "Use two pointers from both ends.", "Track max_left and max_right as you move inward."],
                "test_cases": [{"input": "height=[0,1,0,2,1,0,1,3,2,1,2,1]", "expected": "6"}, {"input": "height=[4,2,0,3,2,5]", "expected": "9"}],
                "solutions": {
                    "python": "def trap(height):\n    left,right=0,len(height)-1\n    maxL=maxR=water=0\n    while left<right:\n        if height[left]<height[right]:\n            if height[left]>=maxL: maxL=height[left]\n            else: water+=maxL-height[left]\n            left+=1\n        else:\n            if height[right]>=maxR: maxR=height[right]\n            else: water+=maxR-height[right]\n            right-=1\n    return water\n\nprint(trap([0,1,0,2,1,0,1,3,2,1,2,1]))  # 6",
                    "javascript": "function trap(height) {\n    let left=0,right=height.length-1,maxL=0,maxR=0,water=0;\n    while(left<right){\n        if(height[left]<height[right]){\n            height[left]>=maxL?(maxL=height[left]):(water+=maxL-height[left]);\n            left++;\n        } else {\n            height[right]>=maxR?(maxR=height[right]):(water+=maxR-height[right]);\n            right--;\n        }\n    }\n    return water;\n}",
                    "java": "class Solution{\n    public int trap(int[] h){\n        int l=0,r=h.length-1,mL=0,mR=0,w=0;\n        while(l<r){\n            if(h[l]<h[r]){\n                if(h[l]>=mL)mL=h[l]; else w+=mL-h[l]; l++;\n            } else {\n                if(h[r]>=mR)mR=h[r]; else w+=mR-h[r]; r--;\n            }\n        }\n        return w;\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
            {
                "id": "23", "title": "Merge K Sorted Lists", "slug": "merge-k-sorted-lists", "difficulty": "Hard", "topic": "Heap, Linked List, Divide and Conquer",
                "description": "Merge k sorted linked lists and return one sorted list.<br><br><strong>Example:</strong><br><code>Input: [[1,4,5],[1,3,4],[2,6]]</code><br><code>Output: [1,1,2,3,4,4,5,6]</code>",
                "hints": ["Use a min-heap of size k.", "Push the head of each list into heap.", "Pop min, add to result, push that node's next."],
                "test_cases": [{"input": "lists=[[1,4,5],[1,3,4],[2,6]]", "expected": "[1,1,2,3,4,4,5,6]"}],
                "solutions": {
                    "python": "import heapq\ndef mergeKLists(lists):\n    heap = []\n    for i, node in enumerate(lists):\n        if node: heapq.heappush(heap, (node.val, i, node))\n    dummy = cur = ListNode(0)\n    while heap:\n        val, i, node = heapq.heappop(heap)\n        cur.next = node; cur = cur.next\n        if node.next: heapq.heappush(heap, (node.next.val, i, node.next))\n    return dummy.next",
                    "javascript": "function mergeKLists(lists) {\n    // Use divide and conquer\n    if (!lists.length) return null;\n    while (lists.length > 1) {\n        const merged = [];\n        for (let i=0;i<lists.length;i+=2)\n            merged.push(mergeTwoLists(lists[i], lists[i+1]||null));\n        lists = merged;\n    }\n    return lists[0];\n}\nfunction mergeTwoLists(l1,l2){\n    const d=new ListNode(0); let c=d;\n    while(l1&&l2){if(l1.val<=l2.val){c.next=l1;l1=l1.next;}else{c.next=l2;l2=l2.next;}c=c.next;}\n    c.next=l1||l2; return d.next;\n}",
                    "java": "class Solution {\n    public ListNode mergeKLists(ListNode[] lists) {\n        PriorityQueue<ListNode> pq=new PriorityQueue<>((a,b)->a.val-b.val);\n        for(ListNode l:lists) if(l!=null) pq.offer(l);\n        ListNode dummy=new ListNode(0),cur=dummy;\n        while(!pq.isEmpty()){\n            cur.next=pq.poll(); cur=cur.next;\n            if(cur.next!=null) pq.offer(cur.next);\n        }\n        return dummy.next;\n    }\n}",
                    "sql": "-- Not a SQL problem",
                },
            },
        ],
    },
    "js": {
        "Easy": [
            {
                "id": "2620", "title": "Counter", "slug": "counter", "difficulty": "Easy", "topic": "Closures",
                "description": "Given integer <code>n</code>, return a counter function that returns <code>n</code> initially, then increments by 1 on each call.<br><br><strong>Example:</strong><br><code>Input: n=10, call 3 times</code><br><code>Output: [10,11,12]</code>",
                "hints": ["Use a closure to capture the variable.", "Return a function that returns n++ each time.", "n++ returns current value then increments."],
                "test_cases": [{"input": "n=10, call×3", "expected": "[10,11,12]"}, {"input": "n=-2, call×5", "expected": "[-2,-1,0,1,2]"}],
                "solutions": {
                    "python": "def createCounter(n):\n    def counter():\n        nonlocal n\n        val = n\n        n += 1\n        return val\n    return counter\n\nc=createCounter(10)\nprint(c(),c(),c())  # 10 11 12",
                    "javascript": "function createCounter(n) {\n    return () => n++;\n}\n\nconst counter = createCounter(10);\nconsole.log(counter()); // 10\nconsole.log(counter()); // 11\nconsole.log(counter()); // 12",
                    "java": "// Java uses AtomicInteger\nimport java.util.concurrent.atomic.AtomicInteger;\nAtomicInteger n = new AtomicInteger(10);\nSupplier<Integer> counter = n::getAndIncrement;",
                    "sql": "-- Not a JS/SQL problem",
                },
            },
            {
                "id": "2635", "title": "Apply Transform Over Each Element", "slug": "apply-transform-over-each-element-in-array", "difficulty": "Easy", "topic": "Array, Functions",
                "description": "Given array <code>arr</code> and function <code>fn</code>, return new array where <code>result[i] = fn(arr[i], i)</code>. Do not use Array.map.<br><br><strong>Example:</strong><br><code>arr=[1,2,3], fn=(x)=>x+1 → [2,3,4]</code>",
                "hints": ["Create empty result array.", "Loop with a for loop (no .map).", "Push fn(arr[i], i) for each index."],
                "test_cases": [{"input": "arr=[1,2,3], fn=(x)=>x+1", "expected": "[2,3,4]"}, {"input": "arr=[1,2,3], fn=(x,i)=>x+i", "expected": "[1,3,5]"}],
                "solutions": {
                    "python": "def map_fn(arr, fn):\n    return [fn(x,i) for i,x in enumerate(arr)]\n\nprint(map_fn([1,2,3], lambda x,i: x+1))  # [2,3,4]",
                    "javascript": "function map(arr, fn) {\n    const result = [];\n    for (let i=0;i<arr.length;i++)\n        result.push(fn(arr[i],i));\n    return result;\n}\n\nconsole.log(map([1,2,3], x => x+1)); // [2,3,4]",
                    "java": "BiFunction<Integer,Integer,Integer> fn = (x,i)->x+1;\nint[] result = new int[arr.length];\nfor(int i=0;i<arr.length;i++) result[i]=fn.apply(arr[i],i);",
                    "sql": "-- Not a SQL problem",
                },
            },
            {
                "id": "2665", "title": "Counter II", "slug": "counter-ii", "difficulty": "Easy", "topic": "Closures, Objects",
                "description": "Return an object with three methods: <code>increment()</code>, <code>decrement()</code>, and <code>reset()</code>. Initial value is <code>init</code>.<br><br><strong>Example:</strong><br><code>init=5, increment→6, reset→5, decrement→4</code>",
                "hints": ["Store current value in closure.", "increment: return ++count, decrement: return --count.", "reset: set count = init, return init."],
                "test_cases": [{"input": "init=5, [increment, reset, decrement]", "expected": "[6,5,4]"}],
                "solutions": {
                    "python": "def createCounter(init):\n    count = [init]\n    return {\n        'increment': lambda: (count.__setitem__(0, count[0]+1), count[0])[1],\n        'decrement': lambda: (count.__setitem__(0, count[0]-1), count[0])[1],\n        'reset':     lambda: (count.__setitem__(0, init), count[0])[1],\n    }",
                    "javascript": "function createCounter(init) {\n    let count = init;\n    return {\n        increment: () => ++count,\n        decrement: () => --count,\n        reset: () => { count = init; return count; },\n    };\n}",
                    "java": "// Use a wrapper class or array to hold mutable state\nint[] count = {init};\nreturn Map.of(\n    \"increment\", (Supplier<Integer>) () -> ++count[0],\n    \"decrement\", (Supplier<Integer>) () -> --count[0],\n    \"reset\",     (Supplier<Integer>) () -> { count[0]=init; return init; }\n);",
                    "sql": "-- Not a SQL problem",
                },
            },
        ],
        "Medium": [
            {
                "id": "2627", "title": "Debounce", "slug": "debounce", "difficulty": "Medium", "topic": "Closures, Timers",
                "description": "Return a debounced version of <code>fn</code> that delays execution by <code>t</code> ms. Cancels if called again within the window.<br><br><strong>Example:</strong><br>Calls at t=20ms and t=100ms with wait=50ms → only 2nd executes at 150ms.",
                "hints": ["Store timer ID in closure.", "clearTimeout on every call.", "setTimeout with fn.apply(this, args)."],
                "test_cases": [{"input": "fn=log, t=20ms, calls at 20ms+100ms", "expected": "Only 2nd call fires"}, {"input": "fn=log, t=50ms, single call", "expected": "Fires at 50ms"}],
                "solutions": {
                    "python": "import threading\n\ndef debounce(fn, t):\n    timer = [None]\n    def debounced(*args):\n        if timer[0]: timer[0].cancel()\n        timer[0] = threading.Timer(t/1000, fn, args)\n        timer[0].start()\n    return debounced",
                    "javascript": "function debounce(fn, t) {\n    let timer;\n    return function(...args) {\n        clearTimeout(timer);\n        timer = setTimeout(() => fn.apply(this, args), t);\n    };\n}\n\nconst log = debounce(console.log, 20);\nlog('a'); // cancelled\nlog('b'); // runs after 20ms",
                    "java": "ScheduledExecutorService ex=Executors.newSingleThreadScheduledExecutor();\nScheduledFuture<?>[] f={null};\nRunnable debounced=()->{\n    if(f[0]!=null)f[0].cancel(false);\n    f[0]=ex.schedule(fn,t,TimeUnit.MILLISECONDS);\n};",
                    "sql": "-- Not a SQL problem",
                },
            },
            {
                "id": "2694", "title": "Event Emitter", "slug": "event-emitter", "difficulty": "Medium", "topic": "Design, OOP",
                "description": "Implement an <code>EventEmitter</code> class with <code>subscribe(event, cb)</code> and <code>emit(event, args)</code>. Subscribe returns an object with <code>unsubscribe()</code>.<br><br><strong>Example:</strong><br><code>emitter.subscribe('x', cb); emitter.emit('x', [5]) → [cb(5)]</code>",
                "hints": ["Use a Map of event → array of callbacks.", "emit calls all callbacks with spread args.", "unsubscribe removes callback from the array."],
                "test_cases": [{"input": "subscribe+emit", "expected": "cb result returned"}, {"input": "unsubscribe then emit", "expected": "no results"}],
                "solutions": {
                    "python": "class EventEmitter:\n    def __init__(self):\n        self.events = {}\n    def subscribe(self, event, cb):\n        self.events.setdefault(event, []).append(cb)\n        def unsubscribe():\n            self.events[event].remove(cb)\n        return type('Sub', (), {'unsubscribe': staticmethod(unsubscribe)})()\n    def emit(self, event, args=[]):\n        return [cb(*args) for cb in self.events.get(event, [])]",
                    "javascript": "class EventEmitter {\n    constructor() { this.events = new Map(); }\n    subscribe(event, cb) {\n        if (!this.events.has(event)) this.events.set(event, []);\n        const subs = this.events.get(event);\n        subs.push(cb);\n        return { unsubscribe: () => { const i=subs.indexOf(cb); if(i>=0)subs.splice(i,1); } };\n    }\n    emit(event, args=[]) {\n        return (this.events.get(event)||[]).map(cb=>cb(...args));\n    }\n}",
                    "java": "// Java implementation using Map<String, List<Function>>\nMap<String, List<Function<Object[],Object>>> events = new HashMap<>();",
                    "sql": "-- Not a SQL problem",
                },
            },
        ],
        "Hard": [
            {
                "id": "2650", "title": "Design Cancellable Function", "slug": "design-cancellable-function", "difficulty": "Hard", "topic": "Promises, Generators",
                "description": "Given async generator <code>fn</code>, return [cancelFn, promise]. If cancelFn() called, generator is cancelled and promise rejects.<br><br><strong>Example:</strong><br><code>const [cancel,p]=cancellable(gen,[5])</code><br><code>setTimeout(cancel,100)</code>",
                "hints": ["Use gen.throw() to cancel the generator.", "Wrap gen.next() in a recursive step() function.", "cancelFn calls gen.throw(new Error('Cancelled'))."],
                "test_cases": [{"input": "generator yields once, cancel at 50ms", "expected": "Promise rejects"}, {"input": "no cancel called", "expected": "Promise resolves with return value"}],
                "solutions": {
                    "python": "import asyncio\nasync def cancellable(gen_fn,args):\n    task=asyncio.create_task(gen_fn(*args))\n    return task.cancel, task",
                    "javascript": "function cancellable(generatorFunction,args){\n    let cancel;\n    const promise=new Promise((resolve,reject)=>{\n        const gen=generatorFunction(...args);\n        cancel=()=>{try{gen.throw(new Error('Cancelled'))}catch(e){} reject('Cancelled');};\n        function step(val){\n            const {done,value}=gen.next(val);\n            if(done) resolve(value);\n            else Promise.resolve(value).then(step).catch(reject);\n        }\n        step();\n    });\n    return [cancel,promise];\n}",
                    "java": "CompletableFuture<Void> future=CompletableFuture.runAsync(fn);\nRunnable cancel=()->future.cancel(true);\nreturn new Object[]{cancel,future};",
                    "sql": "-- Not a SQL problem",
                },
            },
        ],
    },
    "sql": {
        "Easy": [
            {
                "id": "181", "title": "Employees Earning More Than Their Managers", "slug": "employees-earning-more-than-their-managers", "difficulty": "Easy", "topic": "Self Join",
                "description": "<strong>Table: Employee</strong><br><code>id | name | salary | managerId</code><br><br>Find employees who earn more than their managers.<br><br><strong>Example output:</strong> Joe (earns 70000, manager earns 60000)",
                "hints": ["Self-join: Employee e JOIN Employee m ON e.managerId = m.id", "Filter: WHERE e.salary > m.salary", "SELECT e.name AS Employee"],
                "test_cases": [{"input": "Joe(70000,mgr=Sam), Sam(60000)", "expected": "Joe"}],
                "solutions": {
                    "python": "import pandas as pd\ndef find_employees(df):\n    m=df.merge(df,left_on='managerId',right_on='id',suffixes=('_e','_m'))\n    return m[m.salary_e>m.salary_m][['name_e']].rename(columns={'name_e':'Employee'})",
                    "javascript": "-- SQL only",
                    "java": "-- SQL only",
                    "sql": "SELECT e.name AS Employee\nFROM Employee e\nJOIN Employee m ON e.managerId = m.id\nWHERE e.salary > m.salary;",
                },
            },
            {
                "id": "182", "title": "Duplicate Emails", "slug": "duplicate-emails", "difficulty": "Easy", "topic": "GROUP BY, HAVING",
                "description": "<strong>Table: Person</strong><br><code>id | email</code><br><br>Find all emails that appear more than once.<br><br><strong>Example:</strong><br>a@b.com appears twice → output: a@b.com",
                "hints": ["GROUP BY email", "HAVING COUNT(email) > 1", "SELECT email only"],
                "test_cases": [{"input": "[(1,a@b.com),(2,c@d.com),(3,a@b.com)]", "expected": "a@b.com"}],
                "solutions": {
                    "python": "import pandas as pd\ndef duplicate_emails(df):\n    c=df.groupby('email').size().reset_index(name='c')\n    return c[c.c>1][['email']]",
                    "javascript": "-- SQL only",
                    "java": "-- SQL only",
                    "sql": "SELECT email AS Email\nFROM Person\nGROUP BY email\nHAVING COUNT(email) > 1;",
                },
            },
            {
                "id": "197", "title": "Rising Temperature", "slug": "rising-temperature", "difficulty": "Easy", "topic": "Self Join, DATE",
                "description": "<strong>Table: Weather</strong><br><code>id | recordDate | temperature</code><br><br>Find IDs of dates with higher temperature than the previous day.",
                "hints": ["Self-join on DATE_SUB or DATEDIFF.", "JOIN WHERE DATEDIFF(w1.recordDate, w2.recordDate) = 1", "Filter WHERE w1.temperature > w2.temperature"],
                "test_cases": [{"input": "[(1,Jan1,10),(2,Jan2,15),(3,Jan3,12)]", "expected": "[2]"}],
                "solutions": {
                    "python": "import pandas as pd\ndef rising_temp(df):\n    df=df.sort_values('recordDate')\n    df['prev']=df['temperature'].shift(1)\n    df['prev_date']=df['recordDate'].shift(1)\n    mask=(df.temperature>df.prev)&((df.recordDate-df.prev_date).dt.days==1)\n    return df[mask][['id']]",
                    "javascript": "-- SQL only",
                    "java": "-- SQL only",
                    "sql": "SELECT w1.id\nFROM Weather w1\nJOIN Weather w2\n  ON DATEDIFF(w1.recordDate, w2.recordDate) = 1\nWHERE w1.temperature > w2.temperature;",
                },
            },
            {
                "id": "577", "title": "Employee Bonus", "slug": "employee-bonus", "difficulty": "Easy", "topic": "LEFT JOIN, NULL",
                "description": "<strong>Tables: Employee, Bonus</strong><br>Find employees with bonus < 1000 OR no bonus.<br><br><strong>Example:</strong><br>Return name and bonus (NULL if none).",
                "hints": ["Use LEFT JOIN to include employees without bonus.", "WHERE bonus < 1000 OR bonus IS NULL", "Select name, bonus columns"],
                "test_cases": [{"input": "Employee + Bonus tables", "expected": "Employees with bonus<1000 or no bonus"}],
                "solutions": {
                    "python": "import pandas as pd\ndef employee_bonus(emp, bonus):\n    m=emp.merge(bonus,on='empId',how='left')\n    return m[(m.bonus<1000)|m.bonus.isna()][['name','bonus']]",
                    "javascript": "-- SQL only",
                    "java": "-- SQL only",
                    "sql": "SELECT e.name, b.bonus\nFROM Employee e\nLEFT JOIN Bonus b ON e.empId = b.empId\nWHERE b.bonus < 1000 OR b.bonus IS NULL;",
                },
            },
        ],
        "Medium": [
            {
                "id": "176", "title": "Second Highest Salary", "slug": "second-highest-salary", "difficulty": "Medium", "topic": "Subquery, NULL handling",
                "description": "<strong>Table: Employee</strong><br><code>id | salary</code><br><br>Return the second highest salary. Return NULL if none exists.<br><br><strong>Example:</strong><br>Salaries [100,200,300] → 200",
                "hints": ["Use MAX() with WHERE salary < (SELECT MAX(salary)...)", "Or LIMIT 1 OFFSET 1 with ORDER BY salary DESC", "Wrap in SELECT to return NULL when empty"],
                "test_cases": [{"input": "[(1,100),(2,200),(3,300)]", "expected": "200"}, {"input": "[(1,100)]", "expected": "null"}],
                "solutions": {
                    "python": "import pandas as pd\ndef second_highest(df):\n    u=df.salary.drop_duplicates().nlargest(2)\n    return u.iloc[1] if len(u)>=2 else None",
                    "javascript": "-- SQL only",
                    "java": "-- SQL only",
                    "sql": "SELECT MAX(salary) AS SecondHighestSalary\nFROM Employee\nWHERE salary < (SELECT MAX(salary) FROM Employee);",
                },
            },
            {
                "id": "178", "title": "Rank Scores", "slug": "rank-scores", "difficulty": "Medium", "topic": "Window Functions",
                "description": "<strong>Table: Scores</strong><br><code>id | score</code><br><br>Rank scores in descending order. No gaps in ranking (use DENSE_RANK).",
                "hints": ["Use DENSE_RANK() window function.", "DENSE_RANK() OVER (ORDER BY score DESC)", "No gaps: 1,2,2,3 not 1,2,2,4"],
                "test_cases": [{"input": "scores=[3.50,3.65,4.00,3.85,4.00,3.65]", "expected": "ranks=[4,3,1,2,1,3]"}],
                "solutions": {
                    "python": "import pandas as pd\ndef rank_scores(df):\n    df['rank']=df['score'].rank(method='dense',ascending=False).astype(int)\n    return df[['score','rank']].sort_values('rank')",
                    "javascript": "-- SQL only",
                    "java": "-- SQL only",
                    "sql": "SELECT score,\n       DENSE_RANK() OVER (ORDER BY score DESC) AS 'rank'\nFROM Scores\nORDER BY score DESC;",
                },
            },
        ],
        "Hard": [
            {
                "id": "185", "title": "Department Top Three Salaries", "slug": "department-top-three-salaries", "difficulty": "Hard", "topic": "Window Functions, CTE",
                "description": "Find employees who are in the <strong>top 3 unique salaries</strong> in their department.<br><br>Return: Department, Employee, Salary<br><br>Use DENSE_RANK partitioned by department.",
                "hints": ["Use DENSE_RANK() OVER (PARTITION BY departmentId ORDER BY salary DESC)", "Filter WHERE rank <= 3", "JOIN with Department table for dept name"],
                "test_cases": [{"input": "Employee + Department tables", "expected": "Top 3 per department"}],
                "solutions": {
                    "python": "import pandas as pd\ndef top3(emp,dept):\n    m=emp.merge(dept,left_on='departmentId',right_on='id',suffixes=('','_d'))\n    m['rank']=m.groupby('departmentId')['salary'].rank(method='dense',ascending=False)\n    r=m[m['rank']<=3][['name_d','name','salary']]\n    return r.rename(columns={'name_d':'Department','name':'Employee','salary':'Salary'})",
                    "javascript": "-- SQL only",
                    "java": "-- SQL only",
                    "sql": "WITH ranked AS (\n  SELECT e.name, e.salary, d.name AS dept,\n         DENSE_RANK() OVER (PARTITION BY e.departmentId ORDER BY e.salary DESC) AS rnk\n  FROM Employee e JOIN Department d ON e.departmentId = d.id\n)\nSELECT dept AS Department, name AS Employee, salary AS Salary\nFROM ranked WHERE rnk <= 3;",
                },
            },
        ],
    },
}


def pick_daily_questions(difficulty: str, date_seed: int) -> dict:
    rng = random.Random(date_seed)
    result = {}
    for cat in ("dsa", "js", "sql"):
        pool = PROBLEMS[cat].get(difficulty, PROBLEMS[cat]["Easy"])
        q = rng.choice(pool)
        result[cat] = {**q, "category": cat, "link": f"https://leetcode.com/problems/{q['slug']}/"}
    return result

def check_leetcode_solved(username: str, slug: str) -> bool:
    """
    Check via LeetCode GraphQL if the user has an accepted submission for this slug.
    Requires the user's profile to be public.
    """
    query = """
    query recentAcSubmissions($username: String!, $limit: Int!) {
      recentAcSubmissionList(username: $username, limit: $limit) {
        titleSlug
      }
    }
    """
    try:
        scraper = cloudscraper.create_scraper() # <-- USE CLOUDSCRAPER
        resp = scraper.post(
            "https://leetcode.com/graphql",
            json={"query": query, "variables": {"username": username, "limit": 20}},
            headers={"Content-Type": "application/json", "Referer": "https://leetcode.com"},
            timeout=10,
        )
        data = resp.json()
        submissions = data.get("data", {}).get("recentAcSubmissionList", []) or []
        solved_slugs = {s["titleSlug"] for s in submissions}
        return slug in solved_slugs
    except Exception:
        return False