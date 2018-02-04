# C Dynamic Memory Allocation

## What happens when I call malloc?
The function `malloc` is a C library call and is used to reserve a contiguous block of memory. Unlike stack memory, the memory remains allocated until `free` is called with the same pointer. There is also `calloc` and `realloc` which are discussed below.

## Can malloc fail?
If `malloc` fails to reserve any more memory then it returns `NULL`. Robust programs should check the return value. If your code assumes `malloc` succeeds and it does not, then your program will likely crash (segfault) when it tries to write to address 0.

## Where is the heap and how big is it? 
The heap is part of the process memory and it does not have a fixed size. Heap memory allocation is performed by the C library when you call `malloc` (`calloc`, `realloc`) and `free`.

First a quick review on process memory: A process is a running instance of your program. Each process has its own address space. For example on a 32 bit machine your process gets about 4 billion addresses to play with, however not all of these are valid or even mapped to actual physical memory (RAM). Inside the process's memory you will find the executable code, space for the stack, environment variables, global (static) variables and the heap.

By calling `sbrk` the C library can increase the size of the heap as your program demands more heap memory. As the heap and stack (one for each thread) need to grow, we put them at opposite ends of the address space. So for typical architectures the heap will grow upwards and the stack grows downwards. 

Truthiness: Modern operating system memory allocators no longer need `sbrk` - instead they can request independent regions of virtual memory and maintain multiple memory regions. For example gigabyte requests may be placed in a different memory region than small allocation requests. However this detail is an unwanted complexity: The problems of fragmentation and allocating memory efficiently still apply, so we will ignore this implementation nicety here and will write as if the heap is a single region.

If we write a multi-threaded program (more about that later) we will need multiple stacks (one per thread) but there's only ever one heap.

On typical architectures, the heap is part of the `Data segment` and starts just above the code and global variables. 

## Do programs need to call brk or sbrk?
Not typically (though calling `sbrk(0)` can be interesting because it tells you where your heap currently ends). Instead programs use `malloc,calloc,realloc` and `free` which are part of the C library. The internal implementation of these functions will call `sbrk` when additional heap memory is required.
```
void *top_of_heap = sbrk(0);
malloc(16384);
void *top_of_heap2 = sbrk(0);
printf("The top of heap went from %p to %p \n", top_of_heap, top_of_heap2);
```
Example output: `The top of heap went from 0x4000 to 0xa000`


## What is calloc?
Unlike `malloc`, `calloc` initializes memory contents to zero and also takes two arguments (the number of items and the size in bytes of each item). A naive but readable implementation of `calloc` looks like this:
```
void *calloc(size_t n, size_t size)
{
	size_t total = n * size; // Does not check for overflow!
	void *result = malloc(total);
	
	if (!result) return NULL;
	
// If we're using new memory pages 
// just allocated from the system by calling sbrk
// then they will be zero so zero-ing out is unnecessary,

	memset(result, 0, total);
	return result; 
}
```
An advanced discussion of these limitations is [here](http://locklessinc.com/articles/calloc/).

Programmers often use `calloc` rather than explicitly calling `memset` after `malloc`, to set the memory contents to zero. Note `calloc(x,y)` is identical to `calloc(y,x)`, but you should follow the conventions of the manual.

```
// Ensure our memory is initialized to zero
link_t *link  = malloc(256);
memset(link, 0, 256); // Assumes malloc returned a valid address!

link_t *link = calloc(1, 256); // safer: calloc(1, sizeof(link_t));
```
## Why is the memory that is first returned by sbrk initialized to zero?
If the operating system did not zero out contents of physical RAM it might be possible for one process to learn about the memory of another process that had previously used the memory. This would be a security leak.

Unfortunately this means that for `malloc` requests before any memory has been freed and simple programs (which end up using newly reserved memory from the system) the memory is _often_ zero. Then programmers mistaken write C programs that assume malloc'd memory will _always_ be zero.

```
char* ptr = malloc(300);
// contents is probably zero because we get brand new memory
// so beginner programs appear to work!
// strcpy(ptr, "Some data"); // work with the data
free(ptr);
// later
char *ptr2 = malloc(308); // Contents might now contain existing data and is probably not zero
```

## Why doesn't malloc always initialize memory to zero?
Performance! We want malloc to be as fast as possible. Zeroing out memory may be unnecessary.

## What is realloc and when would you use it?
`realloc` allows you to resize an existing memory allocation that was previously allocated on the heap (via malloc,calloc or realloc). The most common use of realloc is to resize memory used to hold an array of values. A naive but readable version of realloc is suggested below
```
void * realloc(void * ptr, size_t newsize) {
  // Simple implementation always reserves more memory
  // and has no error checking
  void *result = malloc(newsize); 
  size_t oldsize =  ... //(depends on allocator's internal data structure)
  if (ptr) memcpy(result, ptr, newsize < oldsize ? newsize : oldsize);
  free(ptr);
  return result;
}
```
An INCORRECT use of realloc is shown below:
```
int *array = malloc(sizeof(int) * 2);
array[0] = 10; array[1] = 20;
// Ooops need a bigger array - so use realloc..
realloc (array, 3); // ERRORS!
array[2] = 30; 
```

The above code contains two mistakes. Firstly we needed 3*sizeof(int) bytes not 3 bytes.
Secondly realloc may need to move the existing contents of the memory to a new location. For example, there may not be sufficient space because the neighboring bytes are already allocated. A correct use of realloc is shown below.
```
array = realloc(array, 3 * sizeof(int));
// If array is copied to a new location then old allocation will be freed.
```
A robust version would also check for a `NULL` return value. Note `realloc` can be used to grow and shrink allocations. 

## Where can I read more?
See [the man page](http://man7.org/linux/man-pages/man3/malloc.3.html)!

## How important is that memory allocation is fast?
Very! Allocating and de-allocating heap memory is a common operation in most applications.

# Intro to Allocating

## What is the silliest malloc and free implementation and what is wrong with it?

```
void* malloc(size_t size)
// Ask the system for more bytes by extending the heap space. 
// sbrk Returns -1 on failure
   void *p = sbrk(size); 
   if(p == (void *) -1) return NULL; // No space left
   return p;
}
void free() {/* Do nothing */}
```
The above implementation suffers from two major drawbacks:
* System calls are slow (compared to library calls). We should reserve a large amount of memory and only occasionally ask for more from the system.
* No reuse of freed memory. Our program never re-uses heap memory - it just keeps asking for a bigger heap.

If this allocator was used in a typical program, the process would quickly exhaust all available memory.
Instead we need an allocator that can efficiently use heap space and only ask for more memory when necessary.

## What are placement strategies?
During program execution memory is allocated and de-allocated (freed), so there will be gaps (holes) in the heap memory that can be re-used for future memory requests. The memory allocator needs to keep track of which parts of the heap are currently allocated and which are parts are available.

Suppose our current heap size is 64K, though not all of it is in use because some earlier malloc'd memory has already been freed by the program: 

16KB free | 10KB allocated | 1KB free | 1KB allocated | 30KB free | 4KB allocated | 2KB free 
---|---|---|---|---|---|---

If a new malloc request for 2KB is executed (`malloc(2048)`), where should `malloc` reserve the memory? It could use the last 2KB hole (which happens to be the perfect size!) or it could split one of the other two free holes. These choices represent different placement strategies.

Whichever hole is chosen, the allocator will need to split the hole into two: The newly allocated space (which will be returned to the program) and a smaller hole (if there is spare space left over).

A perfect-fit strategy finds the smallest hole that is of sufficient size (at least 2KB):

16KB free | 10KB allocated | 1KB free | 1KB allocated | 30KB free | 4KB allocated | '2KB HERE!'
---|---|---|---|---|---|---

A worst-fit strategy finds the largest hole that is of sufficient size (so break the 30KB hole into two):

16KB free | 10KB allocated | 1KB free | 1KB allocated | `2KB HERE!` | `28KB free` | 4KB allocated | 2KB free 
---|---|---|---|---|---|---|---

A first-fit strategy finds the first available hole that is of sufficient size (break the 16KB hole into two):

`2KB HERE!` | `14KB free` | 10KB allocated | 1KB free | 1KB allocated | 30KB free | 4KB allocated | 2KB free 
---|---|---|---|---|---|---|---


## What is external fragmentation?
In the example below, of the 64KB of heap memory, 17KB is allocated, and 47KB is free. However the largest available block is only 30KB because our available unallocated heap memory is fragmented into smaller pieces. 

 `16KB free` | 10KB allocated | 1KB free | 1KB allocated | 30KB free | 4KB allocated | 2KB free 
---|---|---|---|---|---|---

## What effect do placement strategies have on external fragmentation and performance?
Different strategies affect the fragmentation of heap memory in non-obvious ways, which only are discovered by mathematical analysis or careful simulations under real-world conditions (for example simulating the memory allocation requests of a database or webserver).
For example, best-fit at first glance appears to be an excellent strategy however, if we can not find a perfectly-sized hole then this placement creates many tiny unusable holes, leading to high fragmentation. It also requires a scan of all possible holes.

First fit has the advantage that it will not evaluate all possible placements and therefore be faster. 

Since Worst-fit targets the largest unallocated space, it is a poor choice if large allocations are required.

In practice first-fit and next-fit (which is not discussed here) are often common placement strategy. Hybrid approaches and many other alternatives exist (see implementing a memory allocator page).
 
## What are the challenges of writing a heap allocator?
The main challenges are,
* Need to minimize fragmentation (i.e. maximize memory utilization)
* Need high performance
* Fiddly implementation (lots of pointer manipulation using linked lists and pointer arithmetic)

Some additional comments:

Both fragmentation and performance depend on the application allocation profile, which can be evaluated but not predicted and in practice, under-specific usage conditions, a special-purpose allocator can often out-perform a general purpose implementation.

The allocator doesn't know the program's memory allocation requests in advance. Even if we did, this is the [Knapsack problem](http://en.wikipedia.org/wiki/Knapsack_problem) which is known to be NP hard!

# Memory Allocator Tutorial
A memory allocator needs to keep track of which bytes are currently allocated and which are available for use. This page introduces the implementation and conceptual details of building an allocator, i.e. the actual code that implements `malloc` and `free`.

## This page talks about links of blocks - do I malloc memory for them instead?
Though conceptually we are thinking about creating linked lists and lists of blocks, we don't need to "malloc memory" to create them! Instead we are writing integers and pointers into memory that we already control so that we can later consistently hop from one address to the next. This internal information represents some overhead. So even if we had requested 1024 KB of contiguous memory from the system, we will not be able to provide all of it to the running program.

## Thinking in blocks
We can think of our heap memory as a list of blocks where each block is either allocated or unallocated.
Rather than storing an explicit list of pointers we store information about the block's size _as part of the block_. Thus there is conceptually a list of free blocks, but it is implicit, i.e. in the form of block size information that we store as part of each block.

We could navigate from one block to the next block just by adding the block's size. For example if you have a pointer `p` that points to the start of a block, then `next_block`  with be at `((char *)p) +  *(size_t *) p`, if you are storing the size of the blocks in bytes. The cast to `char *` ensures that pointer arithmetic is calculated in bytes. The cast to `size_t *` ensures the memory at `p` is read as a size value and would be necessarily if `p` was a `void *` or `char *` type.

The calling program never sees these values; they are internal to the implementation of the memory allocator. 

As an example, suppose your allocator is asked to reserve 80 bytes (`malloc(80)`) and requires 8 bytes of internal header data. The allocator would need to find an unallocated space of at least 88 bytes. After updating the heap data it would return a pointer to the block. However, the returned pointer does not point to the start of the block because that's where the internal size data is stored! Instead we would return the start of the block + 8 bytes.
In the implementation, remember that pointer arithmetic depends on type. For example, `p += 8` adds `8 * sizeof(p)`, not necessarily 8 bytes!

## Implementing malloc
The simplest implementation uses first fit: Start at the first block, assuming it exists, and iterate until a block that represents unallocated space of sufficient size is found, or we've checked all the blocks.

If no suitable block is found, it's time to call `sbrk()` again to sufficiently extend the size of the heap. A fast implementation might extend it a significant amount so that we will not need to request more heap memory in the near future.

When a free block is found, it may be larger than the space we need. If so, we will create two entries in our implicit list. The first entry is the allocated block, the second entry is the remaining space.

There are two simple ways to note if a block is in use or available. The first is to store it as a byte in the header information along with the size and the second to encode it as the lowest bit in the size!
Thus block size information would be limited to only even values:
```
// Assumes p is a reasonable pointer type, e.g. 'size_t *'.
isallocated = (*p) & 1;
realsize = (*p) & ~1;  // mask out the lowest bit
```

## Alignment and rounding up considerations

Many architectures expect multi-byte primitives to be aligned to some multiple of 2^n. For example, it's common to require 4-byte types to be aligned to 4-byte boundaries (and 8-byte types on 8-byte boundaries). If multi-byte primitives are not stored on a reasonable boundary (for example starting at an odd address) then the performance can be significantly impacted because it may require two memory read requests instead of one. On some architectures the penalty is even greater - the program will crash with a [bus error](http://en.wikipedia.org/wiki/Bus_error#Unaligned_access).

As `malloc` does not know how the user will use the allocated memory (array of doubles? array of chars?), the pointer returned to the program needs to be aligned for the worst case, which is architecture dependent.

From glibc documentation, the glibc `malloc` uses the following heuristic:
"    The block that malloc gives you is guaranteed to be aligned so that it can hold any type of data. On GNU systems, the address is always a multiple of eight on most systems, and a multiple of 16 on 64-bit systems."

For example, if you need to calculate how many 16 byte units are required, don't forget to round up -
```
int s = (requested_bytes + tag_overhead_bytes + 15) / 16
```
The additional constant ensures incomplete units are rounded up. Note, real code is more likely to symbol sizes e.g. `sizeof(x) - 1`, rather than coding numerical constant 15.

[Here's a great article on memory alignment, if you are further interested](http://www.ibm.com/developerworks/library/pa-dalign/)
## A note about internal fragmentation

Internal fragmentation happens when the block you give them is larger than their allocation size. Let's say that we have a free block of size 16B (not including metadata). If they allocate 7 bytes, you may want to round up to 16B and just return the entire block.

This gets very sinister when you implementing coalescing and splitting (next section). If you don't implement either, then you may end up returning a block of size 64B for a 7B allocation! There is a _lot_ of overhead for that allocation which is what we are trying to avoid.

## Implementing free
When `free` is called we need to re-apply the offset to get back to the 'real' start of the block (remember we didn't give the user a pointer to the actual start of the block?), i.e. to where we stored the size information.

A naive implementation would simply mark the block as unused. If we are storing the block allocation status in the lowest size bit, then we just need to clear the bit:
```
*p = (*p) & ~1; // Clear lowest bit 
```
However, we have a bit more work to do: If the current block and the next block (if it exists) are both free we need to coalesce these blocks into a single block.
Similarly, we also need to check the previous block, too. If that exists and represents an unallocated memory, then we need to coalesce the blocks into a single large block.

To be able to coalesce a free block with a previous free block we will also need to find the previous block, so we store the block's size at the end of the block, too. These are called "boundary tags" (ref Knuth73). As the blocks are contiguous, the end of one blocks sits right next to the start of the next block. So the current block (apart from the first one) can look a few bytes further back to lookup the size of the previous block. With this information you can now jump backwards!

## Performance
With the above description it's possible to build a memory allocator. It's main advantage is simplicity - at least simple compared to other allocators!
Allocating memory is a worst-case linear time operation (search linked lists for a sufficiently large free block) and de-allocation is constant time (no more than 3 blocks will need to be coalesced into a single block). Using this allocator it is possible to experiment with different placement strategies. For example, you could start searching from where you last free'd a block, or where you last allocated from. If you do store pointers to blocks, you need to be very careful that they always remain valid (e.g. when coalescing blocks or other malloc or free calls that change the heap structure)

## Explicit Free Lists Allocators

Better performance can be achieved by implementing an explicit doubly-linked list of free nodes. In that case, we can immediately traverse to the next free block and the previous free block. This can halve the search time, because the linked list only includes unallocated blocks.

A second advantage is that we now have some control over the ordering of the linked list. For example, when a block is free'd, we could choose to insert it into the beginning of the linked list rather than always between its neighbors. This is discussed below.

Where do we store the pointers of our linked list? A simple trick is to realize that the block itself is not being used and store the next and previous pointers as part of the block (though now you have to ensure that the free blocks are always sufficiently large to hold two pointers).

We still need to implement Boundary Tags (i.e. an implicit list using sizes), so that we can correctly free blocks and coalesce them with their two neighbors. Consequently, explicit free lists require more code and complexity.

With explicit linked lists a fast and simple 'Find-First' algorithm is used to find the first sufficiently large link. However, since the link order can be modified, this corresponds to different placement strategies. For example if the links are maintained from largest to smallest, then this produces a 'Worst-Fit' placement strategy.

### Explicit linked list insertion policy
The newly free'd block can be inserted easily into two possible positions: at the beginning or in address order (by using the boundary tags to first find the neighbors).

Inserting at the beginning creates a LIFO (last-in, first-out) policy: The most recently free'd spaces will be reused. Studies suggest fragmentation is worse than using address order.

Inserting in address order ("Address ordered policy") inserts free'd blocks so that the blocks are visited in increasing address order. This policy required more time to free a block because the boundary tags (size data) must be used to find the next and previous unallocated blocks. However, there is less fragmentation.

# Case study: Buddy Allocator (an example of a segregated list)

A segregated allocator is one that divides the heap into different areas that are handled by different sub-allocators dependent on the size of the allocation request. Sizes are grouped into classes (e.g. powers of two) and each size is handled by a different sub-allocator and each size maintains its own free list.

A well known allocator of this type is the buddy allocator. We'll discuss the binary buddy allocator which splits allocation into blocks of size 2^n (n = 1, 2, 3, ...) times some base unit number of bytes, but others also exist (e.g. Fibonacci split - can you see why it's named?). The basic concept is simple: If there are no free blocks of size 2^n, go to the next level and steal that block and split it into two. If two neighboring blocks of the same size become unallocated, they can be coalesced back together into a single large block of twice the size.

Buddy allocators are fast because the neighboring blocks to coalesce with can be calculated from the free'd block's address, rather than traversing the size tags. Ultimate performance often requires a small amount of assembler code to use a specialized CPU instruction to find the lowest non-zero bit. 

The main disadvantage of the Buddy allocator is that they suffer from *internal fragmentation*, because allocations are rounded up to the nearest block size. For example, a 68-byte allocation will require a 128-byte block.



### Further Reading and References
* See [Foundations of Software Technology and Theoretical Computer Science 1999 proceedings](http://books.google.com/books?id=0uHME7EfjQEC&lpg=PP1&pg=PA85#v=onepage&q&f=false) (Google books,page 85)
* ThanksForTheMemory UIUC lecture Slides ([pptx](https://subversion.ews.illinois.edu/svn/sp17-cs241/_shared/wikifiles/CS241-05-ThanksForTheMemorySlides.pptx)) ([pdf](https://subversion.ews.illinois.edu/svn/sp17-cs241/_shared/wikifiles/CS241-05-ThanksForTheMemorySlides.pdf))
and 
* [Wikipedia's buddy memory allocation page](http://en.wikipedia.org/wiki/Buddy_memory_allocation)

# Other allocators
There are many other allocation schemes. For example [SLUB](http://en.wikipedia.org/wiki/SLUB_%28software%29) (wikipedia) - one of three allocators used internally by the Linux Kernel.

# Stack Smashing
Each thread uses a stack memory. The stack 'grows downwards' - if a function calls another function, then the stack is extended to smaller memory addresses.
Stack memory includes non-static automatic (temporary) variables, parameter values and the return address.
If a buffer is too small some data (e.g. input values from the user), then there is a real possibility that other stack variables and even the return address will be overwritten.
The precise layout of the stack's contents and order of the automatic variables is architecture and compiler dependent. However with a little investigative work we can learn how to deliberately smash the stack for a particular architecture.

The example below demonstrates how the return address is stored on the stack. For a particular 32 bit architecture [Live Linux Machine](http://cs-education.github.io/sys/), we determine that the return address is stored at an address two pointers (8 bytes) above the address of the automatic variable. The code deliberately changes the stack value so that when the input function returns, rather than continuing on inside the main method, it jumps to the exploit function instead.


````
// Overwrites the return address on the following machine:
// http://cs-education.github.io/sys/
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void breakout() {
    puts("Welcome. Have a shell...");
    system("/bin/sh");
}
void input() {
  void *p;
  printf("Address of stack variable: %p\n", &p);
  printf("Something that looks like a return address on stack: %p\n", *((&p)+2));
  // Let's change it to point to the start of our sneaky function.
  *((&p)+2) = breakout;
}
int main() {
    printf("main() code starts at %p\n",main);
    
    input();
    while (1) {
        puts("Hello");
        sleep(1);
    }

    return 0;
}
````

There are [a lot](https://en.wikipedia.org/wiki/Stack_buffer_overflow) of ways that computers tend to get around this.

# Topics
* Best Fit
* Worst Fit
* First Fit
* Buddy Allocator
* Internal Fragmentation
* External Fragmentation
* sbrk
* Natural Alignment
* Boundary Tag
* Coalescing
* Splitting
* Slab Allocation/Memory Pool

# Questions/Exercises
* What is Internal Fragmentation? When does it become an issue?
* What is External Fragmentation? When does it become an issue?
* What is a Best Fit placement strategy? How is it with External Fragmentation? Time Complexity?
* What is a Worst Fit placement strategy? Is it any better with External Fragmentation? Time Complexity?
* What is the First Fit Placement strategy? It's a little bit better with Fragmentation, right? Expected Time Complexity?
* Let's say that we are using a buddy allocator with a new slab of 64kb. How does it go about allocating 1.5kb?
* When does the 5 line `sbrk` implementation of malloc have a use?
* What is natural alignment?
* What is Coalescing/Splitting? How do they increase/decrease fragmentation? When can you coalesce or split?
* How do boundary tags work? How can they be used to coalesce or split?
