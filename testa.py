from typing import List, Optional


def removeDuplicates(nums: List[int], val: int) -> int:
    k = 0  # k represents the length of the new array without duplicates
    for i in range(len(nums)):
        if nums[i] == val:
            nums.pop(i)
            nums.append(val)

    for i in range(len(nums)):
        if nums[i] != val:
            k += 1
    print(nums)
    nums = nums[0:k]

    return k


print(removeDuplicates([0, 1, 2, 2, 3, 0, 4, 2], val=2))
