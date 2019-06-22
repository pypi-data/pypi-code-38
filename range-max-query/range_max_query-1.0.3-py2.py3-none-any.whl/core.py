import sys

class SegmentTreeNode:
    def __init__(self, start, end, max_val):
        """
        segment tree node structure
        @param: int start
        @param: int end
        @param: int/double max_val

        """
        self.start = start
        self.end = end 
        self.max = max_val
        self.left = None
        self.right = None


class RangeMaxQuery:
    def __init__(self, A):
        """
        initialize the data stucture
        @param: list A
        """
        
        self.root = self.build_helper(0, len(A) - 1, A)

    def build_helper(self, left, right, A):
        """
        build the data structure
        @param: int left: left index
        @param: int right: right index
        @param: list A

        """
        if left > right:
            return None 

        root = SegmentTreeNode(left, right, A[left])

        if left == right:
            return root 

        mid = (left + right) // 2
        root.left = self.build_helper(left, mid, A)
        root.right = self.build_helper(mid+1, right, A)
        root.max = max(root.left.max, root.right.max)

        return root 

    def update(self, index, value):
        """
        update value at index
        @param: int index
        @param: double/int value

        """
        self._modify(self.root, index, value)
        

    def _modify(self, root, index, value):
        """
        helper funcf for updating new value
        @param: SegmentTreeNode root
        @param: int index
        @param: int/double value

        """
        if root.start == root.end and root.start == index:
            root.max = value
            return

        mid = (root.start + root.end) // 2
        if index <= mid:
            self._modify(root.left, index, value)
            root.max = max(root.left.max, root.right.max)
        else:
            self._modify(root.right, index, value)
            root.max = max(root.left.max, root.right.max)
        return

    def range_max_query(self, start, end):
        """
        maximum value query in range(start, end)
        @param: int start
        @param: int end
        """
        return self._max_query(self.root, start, end)
        
    def _max_query(self, root, start, end):
        """
        help func for range max query
        @param: SegmentTreeNode root
        @param: int start
        @param: int end

        """
        if start <= root.start and root.end <= end:
            return root.max
        mid = (root.start + root.end) // 2
        ans = -sys.maxsize
        if mid >= start:
            ans = max(ans, self._max_query(root.left, start, end))
        if mid + 1 <= end:
            ans = max(ans, self._max_query(root.right, start, end))
        return ans


        










