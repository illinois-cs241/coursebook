# What is Virtual Memory?

In very simple embedded systems and early computers, processes directly access memory i.e. "Address 1234" corresponds to a particular byte stored in a particular part of physical memory.
In modern systems, this is no longer the case. Instead each process is isolated; and there is a translation process between the address of a particular CPU instruction or piece of data of a process and the actual byte of physical memory ("RAM"). Memory addresses are no longer 'real'; the process runs inside virtual memory. Virtual memory not only keeps processes safe (because one process cannot directly read or modify another process's memory) it also allows the system to efficiently allocate and re-allocate portions of memory to different processes.

## What is the MMU?
The Memory Management Unit is part of the CPU. It converts a virtual memory address into a physical address. The MMU may also interrupt the CPU if there is currently no mapping from a particular virtual address to a physical address or if the current CPU instruction attempts to write to location that the process only has read-access.

## So how do we convert a virtual address into a physical address?
Imagine you had a 32 bit machine. Pointers can hold 32 bits i.e. they can address 2^32 different locations i.e. 4GB of memory (we will be following the standard convention of one address can hold one byte).

Imagine we had a large table - here's the clever part - stored in memory! For every possible address (all 4 billion of them) we will store the 'real' i.e. physical address. Each physical address will need 4 bytes (to hold the 32 bits).
This scheme would require 16 billion bytes to store all of entries. Oops - our lookup scheme would consume all of the memory that we could possibly buy for our 4GB machine.
We need to do better than this. Our lookup table better be smaller than the memory we have otherwise we will have no space left for our actual programs and operating system data.
The solution is to chunk memory into small regions called 'pages' and 'frames' and use a lookup table for each page.
# What is a page? How many of them are there?

A page is a block of virtual memory. A typical block size on Linux operating system is 4KB (i.e. 2^12 addresses), though you can find examples of larger blocks.

So rather than talking about individual bytes we can talk about blocks of 4KBs, each block is called a page. We can also number our pages ("Page 0" "Page 1" etc)

## EX: How many pages are there in a 32bit machine (assume page size of 4KB)?
Answer: 2^32 address / 2^12 = 2^20 pages.

Remember that 2^10 is 1024, so 2^20 is a bit more than one million.

For a 64 bit machine, 2^64 / 2^12 = 2^52, which is roughly 10^15 pages.

## What is a frame?
A frame (or sometimes called a 'page frame') is a block of _physical memory_ or RAM (=Random Access Memory). This kind of memory is occasionally called 'primary storage' (and contrasted with slower, secondary storage such as spinning disks that have lower access times)

A frame is the same number of bytes as a virtual page. If a 32 bit machine has 2^32 (4GB) of RAM, then there will be the same number of them in the addressable space of the machine. It's unlikely that a 64 bit machine will ever have 2^64 bytes of RAM - can you see why?

## What is a page table and how big is it?
A page table is a mapping between a page to the frame.
For example Page 1 might be mapped to frame 45, page 2 mapped to frame 30. Other frames might be currently unused or assigned to other running processes, or used internally by the operating system.

A simple page table is just an array, `int frame = table[ page_num ];`

For a 32 bit machine with 4KB pages, each entry needs to hold a frame number - i.e. 20 bits because we calculated there are 2^20 frames. That's 2.5 bytes per entry! In practice, we'll round that up to 4 bytes per entry and find a use for those spare bits. With 4 bytes per entry x 2^20 entries = 4 MB of physical memory are required to hold the page table.

For a 64 bit machine with 4KB pages, each entry needs 52 bits. Let's round up to 64 bits (8 bytes) per entry. With 2^52 entries thats 2^55 bytes (roughly 40 peta bytes...) Oops our page table is too large.

In 64 bit architectures memory addresses are sparse, so we need a mechanism to reduce the page table size, given that most of the entries will never be used.

![](http://www.cs.odu.edu/~cs471w/spring12/lectures/MainMemory_files/image028.jpg)

A visual example of the page table is here. Imagine accessing an array and grabbing array elements.

## What is the offset and how is it used?
Remember our page table maps pages to frames, but each page is a block of contiguous addresses. How do we calculate which particular byte to use inside a particular frame? The solution is to re-use the lowest bits of the virtual memory address directly. For example, suppose our process is reading the following address-
```VirtualAddress = 11110000111100001111000010101010 (binary)```

On a machine with page size 256 Bytes, then the lowest 8 bits (10101010) will be used as the offset.
The remaining upper bits will be the page number (111100001111000011110000).


## Multi-level page tables
Multi-level pages are one solution to the page table size issue for 64 bit architectures. We'll look at the simplest implementation - a two level page table. Each table is a list of pointers that point to the next level of tables, not all sub-tables need to exist. An example, two level page table for a 32 bit architecture is shown below-

```
VirtualAddress = 11110000111111110000000010101010 (binary)
                 |_Index1_||        ||          | 10 bit Directory index
                           |_Index2_||          | 10 bit Sub-table index
                                     |__________| 12 bit offset (passed directly to RAM)
```
In the above scheme, determining the frame number requires two memory reads: The topmost 10 bits are used in a directory of page tables. If 2 bytes are used for each entry, we only need 2KB to store this entire directory. Each subtable will point to physical frames (i.e. required 4 bytes to store the 20 bits). However, for processes with only tiny memory needs, we only need to specify entries for low memory address (for the heap and program code) and high memory addresses (for the stack). Each subtable is 1024 entries x 4 bytes i.e. 4KB for each subtable. 

Thus the total memory overhead for our multi-level page table has shrunk from 4MB (for the single level implementation) to 3 frames of memory (12KB) ! Here's why: We need at least one frame for the high level directory and two frames for just two sub-tables. One sub-table is necessary for the low addresses (program code, constants and possibly a tiny heap), the other sub-table is for higher addresses used by the environment and stack. In practice, real programs will likely need more sub-table entries, as each subtable can only reference 1024\*4KB = 4MB of address space but the main point still stands - we have significantly reduced the memory overhead required to perform page table look ups.


## Do page tables make memory access slower? (And what's a TLB)

Yes - Significantly ! (But thanks to clever hardware, usually no...)
Compared to reading or writing memory directly.
For a single page table, our machine is now twice as slow! (Two memory accesses are required)
For a two-level page table, memory access is now three times as slow. (Three memory accesses are required)

To overcome this overhead, the MMU includes an associative cache of recently-used  virtual-page-to-frame lookups. This cache is called the TLB ("translation lookaside buffer"). Everytime a virtual address needs to be translated into a physical memory location, the TLB is queried in parallel to the page table. For most memory accesses of most programs, there is a significant chance that the TLB has cached the results. However if a program does not have good cache coherence (for example is reading from random memory locations of many different pages) then the TLB will not have the result cache and now the MMU must use the much slower page table to determine the physical frame.

![](https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/X86_Paging_4K.svg/440px-X86_Paging_4K.svg.png)

This may be how one splits up a multi level page table.

# Advanced Frames and Page Protections

## Can frames be shared between processes? Can they be specialized
Yes! In addition to storing the frame number, the page table can be used to store whether a process can write or only read a particular frame. Read only frames can then be safely shared between multiple processes. For example, the C-library instruction code can be shared between all processes that dynamically load the code into the process memory. Each process can only read that memory. Meaning that if you try to write to a read-only page in memory you will get a `SEGFAULT`. That is why sometimes memory accesses segfault and sometimes they don't, it all depends on if your hardware says that you can access.

In addition, processes can share a page with a child process using the `mmap` system call. `mmap` is an interesting call because instead of tying each virtual address to a physical frame, it ties it to something else. That something else can be a file, a GPU unit, or any other memory mapped operation that you can think of! Writing to the memory address may write through to the device or the write may be paused by the operating system but this is a very powerful abstraction because often the operating system is able to perform optimizations (multiple processes memory mapping the same file can have the kernel create one mapping).

## What else is stored in the page table and why?
In addition to read-only bit and usage statistics discussed above, it is common to store at least read-only, modification and execution information. 

## What's a page fault?
A page fault is when a running program tries to access some virtual memory in its address space that is not mapped to physical memory. Page faults will also occur in other situations.

There are three types of Page Faults

**Minor** If there is no mapping yet for the page, but it is a valid address. This could be memory asked for by `sbrk(2)` but not written to yet meaning that the operating system can wait for the first write before allocating space. The OS simply makes the page, loads it into memory, and moves on.

**Major** If the mapping to the page is not in memory but on disk. What this will do is swap the page into memory and swap another page out. If this happens frequently enough, your program is said to _thrash_ the MMU.

**Invalid** When you try to write to a non-writable memory address or read to a non-readable memory address. The MMU generates an invalid fault and the OS will usually generate a `SIGSEGV` meaning segmentation violation meaning that you wrote outside the segment that you could write to.

### Read-only bit
The read-only bit marks the page as read-only. Attempts to write to the page will cause a page fault. The page fault will then be handled by the Kernel. Two examples of the read-only page include sharing the c runtime library between multiple processes (for security you wouldn't want to allow one process to modify the library); and Copy-On-Write where the cost of duplicating a page can be delayed until the first write occurs. 

### Dirty bit
http://en.wikipedia.org/wiki/Page_table#Page_table_data
> The dirty bit allows for a performance optimization. A page on disk that is paged in to physical memory, then read from, and subsequently paged out again does not need to be written back to disk, since the page hasn't changed. However, if the page was written to after it's paged in, its dirty bit will be set, indicating that the page must be written back to the backing store. This strategy requires that the backing store retain a copy of the page after it is paged in to memory. When a dirty bit is not used, the backing store need only be as large as the instantaneous total size of all paged-out pages at any moment. When a dirty bit is used, at all times some pages will exist in both physical memory and the backing store.

### Execution bit
The execution bit defines whether bytes in a page can be executed as CPU instructions. By disabling a page, it prevents code that is maliciously stored in the process memory (e.g. by stack overflow) from being easily executed. (further reading: http://en.wikipedia.org/wiki/NX_bit#Hardware_background)


### Find out more
A lower level more and more technical discussion of paging and page bits on x86 platform is discussed at [http://wiki.osdev.org/Paging]

## What is IPC?

Inter process communication is any way for one process to talk to another process. You've already seen one form of this virtual memory! A piece of virtual memory can be shared between parent and child, leading to communication. You may want to wrap that memory in `pthread_mutexattr_setpshared(&attrmutex, PTHREAD_PROCESS_SHARED);` mutex (or a process wide mutex) to prevent race conditions.

There are more standard ways of IPC, like pipes! Consider if you type the following into your terminal

```bash
$ ls -1 | cut -d'.' -f1 | uniq | sort | tee dir_contents
```

What does the following code do (It doesn't really matter so you can skip this if you want)? Well it `ls`'s the current directory (the -1 means that it outputs one entry per line). The `cut` command then takes everything before the first period. Uniq makes sure all the lines are uniq, sort sorts them and tee outputs to a file. 

The important part is that bash creates **5 separate processes** and connects their standard outs/stdins with pipes the trail looks something like this.

(0) ls (1)------>(0) cut (1)------->(0) uniq (1)------>(0) sort (1)------>(0) tee (1)

The numbers in the pipes are the file descriptors for each process and the arrow represents the redirect or where the output of the pipe is going.

## What is a pipe?

A POSIX pipe is almost like its real counterpart - you can stuff bytes down one end and they will appear at the other end in the same order. Unlike real pipes however, the flow is always in the same direction, one file descriptor is used for reading and the other for writing. The `pipe` system call is used to create a pipe.
```C
int filedes[2];
pipe (filedes);
printf("read from %d, write to %d\n", filedes[0], filedes[1]);
```

These file descriptors can be used with `read` -
```C
// To read...
char buffer[80];
int bytesread = read(filedes[0], buffer, sizeof(buffer));
```
And `write` - 
```C
write(filedes[1], "Go!", 4);
```

## How can I use pipe to communicate with a child process?
A common method of using pipes is to create the pipe before forking.
```C
int filedes[2];
pipe (filedes);
pid_t child = fork();
if (child > 0) { /* I must be the parent */
    char buffer[80];
    int bytesread = read(filedes[0], buffer, sizeof(buffer));
    // do something with the bytes read    
}
```

The child can then send a message back to the parent:
```C
if (child == 0) {
   write(filedes[1], "done", 4);
}
```
## Can I use pipes inside a single process?
Short answer: Yes, but I'm not sure why you would want to LOL!

Here's an example program that sends a message to itself:
```C
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

int main() {
    int fh[2];
    pipe(fh);
    FILE *reader = fdopen(fh[0], "r");
    FILE *writer = fdopen(fh[1], "w");
    // Hurrah now I can use printf rather than using low-level read() write()
    printf("Writing...\n");
    fprintf(writer,"%d %d %d\n", 10, 20, 30);
    fflush(writer);
    
    printf("Reading...\n");
    int results[3];
    int ok = fscanf(reader,"%d %d %d", results, results + 1, results + 2);
    printf("%d values parsed: %d %d %d\n", ok, results[0], results[1], results[2]);
    
    return 0;
}
```

The problem with using a pipe in this fashion is that writing to a pipe can block i.e. the pipe only has a limited buffering capacity. If the pipe is full the writing process will block! The maximum size of the buffer is system dependent; typical values from  4KB upto 128KB.

```C
int main() {
    int fh[2];
    pipe(fh);
    int b = 0;
    #define MESG "..............................."
    while(1) {
        printf("%d\n",b);
        write(fh[1], MESG, sizeof(MESG))
        b+=sizeof(MESG);
    }
    return 0;
}
```

# Pipe Gotchas
Here's a complete example that doesn't work! The child reads one byte at a time from the pipe and prints it out - but we never see the message! Can you see why?

```C
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

int main() {
    int fd[2];
    pipe(fd);
    //You must read from fd[0] and write from fd[1]
    printf("Reading from %d, writing to %d\n", fd[0], fd[1]);

    pid_t p = fork();
    if (p > 0) {
        /* I have a child therefore I am the parent*/
        write(fd[1],"Hi Child!",9);

        /*don't forget your child*/
        wait(NULL);
    } else {
        char buf;
        int bytesread;
        // read one byte at a time.
        while ((bytesread = read(fd[0], &buf, 1)) > 0) {
            putchar(buf);
        }
    }
    return 0;
}

```
The parent sends the bytes `H,i,(space),C...!` into the pipe (this may block if the pipe is full).
The child starts reading the pipe one byte at a time. In the above case, the child process will read and print each character. However it never leaves the while loop! When there are no characters left to read it simply blocks and waits for more. 

The call `putchar` writes the characters out but we never flush the `stdout` buffer. i.e. We have transferred the message from one process to another but it has not yet been printed. To see the message we could flush the buffer e.g. `fflush(stdout)` (or `printf("\n")` if the output is going to a terminal). A better solution would also exit the loop by checking for an end-of-message marker,
```C
        while ((bytesread = read(fd[0], &buf, 1)) > 0) {
            putchar(buf);
            if (buf == '!') break; /* End of message */
        }
```
And the message will be flushed to the terminal when the child process exits.


## Want to use pipes with printf and scanf? Use fdopen!

POSIX file descriptors are simple integers 0,1,2,3...
At the C library level, C wraps these with a buffer and useful functions like printf and scanf, so we that we can easily print or parse integers, strings etc.
If you already have a file descriptor then you can 'wrap' it yourself into a FILE pointer using `fdopen` :


```C
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

int main() {
    char *name="Fred";
    int score = 123;
    int filedes = open("mydata.txt", "w", O_CREAT, S_IWUSR | S_IRUSR);

    FILE *f = fdopen(filedes, "w");
    fprintf(f, "Name:%s Score:%d\n", name, score);
    fclose(f);
```
For writing to files this is unnecessary - just use `fopen` which does the same as `open` and `fdopen`
However for pipes, we already have a file descriptor - so this is great time to use `fdopen`!

Here's a complete example using pipes that almost works! Can you spot the error? Hint: The parent never prints anything!

```C
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>

int main() {
    int fh[2];
    pipe(fh);
    FILE *reader = fdopen(fh[0], "r");
    FILE *writer = fdopen(fh[1], "w");
    pid_t p = fork();
    if (p > 0) {
        int score;
        fscanf(reader, "Score %d", &score);
        printf("The child says the score is %d\n", score);
    } else {
        fprintf(writer, "Score %d", 10 + 10);
        fflush(writer);
    }
    return 0;
}
```
Note the (unnamed) pipe resource will disappear once both the child and parent have exited. In the above example the child will send the bytes and the parent will receive the bytes from the pipe. However, no end-of-line character is ever sent, so `fscanf` will continue to ask for bytes because it is waiting for the end of the line i.e. it will wait forever! The fix is to ensure we send a newline character, so that `fscanf` will return.
```C
change:   fprintf(writer, "Score %d", 10 + 10);
to:       fprintf(writer, "Score %d\n", 10 + 10);
```

## So do we need to `fflush` too?
Yes, if you want your bytes to be sent to the pipe immediately! At the beginning of this course we assumed that file streams are always _line buffered_ i.e. the C library will flush its buffer everytime you send a newline character. Actually this is only true for terminal streams - for other filestreams the C library attempts to improve performance by only flushing when it's internal buffer is full or the file is closed.


## When do I need two pipes?

If you need to send data to and from a child asynchronously, then two pipes are required (one for each direction).
Otherwise the child would attempt to read its own data intended for the parent (and vice versa)!

## Closing pipes gotchas

Processes receive the signal SIGPIPE when no process is listening! From the pipe(2) man page - 
```
If all file descriptors referring to the read end of a pipe have been closed,
 then a write(2) will cause a SIGPIPE signal to be generated for the calling process. 
```

Tip: Notice only the writer (not a reader) can use this signal.
To inform the reader that a writer is closing their end of the pipe, you could write your own special byte (e.g. 0xff) or a message ( `"Bye!"`)

Here's an example of catching this signal that does not work! Can you see why?
```C
#include <stdio.h>
#include <stdio.h>
#include <unistd.h>
#include <signal.h>

void no_one_listening(int signal) {
    write(1, "No one is listening!\n", 21);
}

int main() {
    signal(SIGPIPE, no_one_listening);
    int filedes[2];
    
    pipe(filedes);
    pid_t child = fork();
    if (child > 0) { 
        /* I must be the parent. Close the listening end of the pipe */
        /* I'm not listening anymore!*/
        close(filedes[0]);
    } else {
        /* Child writes messages to the pipe */
        write(filedes[1], "One", 3);
        sleep(2);
        // Will this write generate SIGPIPE ?
        write(filedes[1], "Two", 3);
        write(1, "Done\n", 5);
    }
    return 0;
}
```
The mistake in above code is that there is still a reader for the pipe! The child still has the pipe's first file descriptor open and remember the specification? All readers must be closed.

When forking, _It is common practice_ to close the unnecessary (unused) end of each pipe in the child and parent process. For example the parent might close the reading end and the child might close the writing end (and vice versa if you have two pipes)

## What is filling up the pipe? What happens when the pipe becomes full?

A pipe gets filled up when the writer writes too much to the pipe without the reader reading any of it. When the pipes become full, all writes fail until a read occurs. Even then, a write may partial fail if the pipe has a little bit of space left but not enough for the entire message.

To avoid this, usually two things are done. Either increase the size of the pipe. Or more commonly, fix your program design so that the pipe is constantly being read from.

## Are pipes process safe?

Yes! Pipe write are atomic up to the size of the pipe. Meaning that if two processes try to write to the same pipe, the kernel has internal mutexes with the pipe that it will lock, do the write, and return. The only gotcha is when the pipe is about to become full. If two processes are trying to write and the pipe can only satisfy a partial write, that pipe write is not atomic -- be careful about that!

## The lifetime of pipes

Unnamed pipes (the kind we've seen up to this point) live in memory (do not take up any disk space) and are a simple and efficient form of inter-process communication (IPC) that is useful for streaming data and simple messages. Once all processes have closed, the pipe resources are freed.

An alternative to _unamed_ pipes is _named_ pipes created using `mkfifo`.

# Named Pipes

## How do I create named pipes?

From the command line: `mkfifo`
From C: `int mkfifo(const char *pathname, mode_t mode);`

You give it the path name and the operation mode, it will be ready to go! Named pipes take up no space on the disk. What the operating system is essentially telling you when you have a named pipe is that it will create an unnamed pipe that refers to the named pipe, and that's it! There is no additional magic. This is just for programming convenience if processes are started without forking (meaning that there would be no way to get the file descriptor to the child process for an unnamed pipe)

## Why is my pipe hanging?
Reads and writes hang on Named Pipes until there is at least one reader and one writer, take this
```bash
1$ mkfifo fifo
1$ echo Hello > fifo
# This will hang until I do this on another terminal or another process
2$ cat fifo
Hello
```
Any `open` is called on a named pipe the kernel blocks until another process calls the opposite open. Meaning, echo calls `open(.., O_RDONLY)` but that blocks until cat calls `open(.., O_WRONLY)`, then the programs are allowed to continue.

## Race condition with named pipes.
What is wrong with the following program?

```C
//Program 1

int main(){
	int fd = open("fifo", O_RDWR | O_TRUNC);
	write(fd, "Hello!", 6);
	close(fd);
	return 0;
}

//Program 2
int main() {
	char buffer[7];
	int fd = open("fifo", O_RDONLY);
	read(fd, buffer, 6);
	buffer[6] = '\0';
	printf("%s\n", buffer);
	return 0;
}
```

This may never print hello because of a race condition. Since you opened the pipe in the first process under both permissions, open won't wait for a reader because you told the operating system that you are a reader! Sometimes it looks like it works because the execution of the code looks something like this.

| Process 1 | Process 2 |
|-----------|-----------|
|  open(O_RDWR) & write()  |           |
|           |   open(O_RDONLY) & read()  |
|  close() & exit()   |           |
|           | print() & exit() |


Sometimes it won't

| Process 1 | Process 2 |
|-----------|-----------|
|  open(O_RDWR) & write()  |           |
|  close() & exit()   |  (Named pipe is destroyed)  |
|   (Blocks indefinitely)        |    open(O_RDONLY)       |


## Two types of files

On linux, there are two abstractions with files. The first is the linux `fd` level abstraction that means you can use
* `open`
* `read`
* `write`
* `close`
* `lseek`
* `fcntl`
...

And so on. The linux interface is very powerful and expressive, but sometimes we need portability (for example if we are writing for a mac or windows). This is where C's abstraction comes into play. On different operating systems, C uses the low level functions to create a wrapper around files you can use everywhere, meaning that C on linux uses the above calls. C has a few of the following
* `fopen`
* `fread` or `fgetc/fgets` or `fscanf`
* `fwrite` or `fprintf`
* `fclose`
* `fflush`

But you don't get the expressiveness that linux gives you with system calls you can convert back and forth between them with `int fileno(FILE* stream)` and `FILE* fdopen(int fd...)`.

Another important aspect to note is the C files are **buffered** meaning that their contents may not be written right away by default. You can can change that with C options.

## How do I tell how large a file is?
For files less than the size of a long, using fseek and ftell is a simple way to accomplish this:

Move to the end of the file and find out the current position.
```C
fseek(f, 0, SEEK_END);
long pos = ftell(f);
```
This tells us the current position in the file in bytes - i.e. the length of the file!

`fseek` can also be used to set the absolute position.
```C
fseek(f, 0, SEEK_SET); // Move to the start of the file 
fseek(f, posn, SEEK_SET);  // Move to 'posn' in the file.
```
All future reads and writes in the parent or child processes will honor this position.
Note writing or reading from the file will change the current position.

See the man pages for fseek and ftell for more information.

## But try not to do this
**Note: This is not recommended in the usual case because of a quirk with the C language**. That quirk is that longs only need to be **4 Bytes big** meaning that the maximum size that ftell can return is a little under 2 Gigabytes (which we know nowadays our files could be hundreds of gigabytes or even terabytes on a distributed file system). What should we do instead? Use `stat`! We will cover stat in a later part but here is some code that will tell you the size of the file
```C
struct stat buf;
if(stat(filename, &buf) == -1){
	return -1;
}
return (ssize_t)buf.st_size;
```
buf.st_size is of type off_t which is big enough for _insanely_ large files.

## What happens if a child process closes a filestream using `fclose` or `close`?
Closing a file stream is unique to each process. Other processes can continue to use their own file-handle. Remember, everything is copied over when a child is created, even the relative positions of the files.

## How about mmap for files?

One of the general uses for mmap is to map a file to memory. This does not mean that the file is malloc'ed to memory right away. Take the following code for example.

```
int fd = open(...); //File is 2 Pages
char* addr = mmap(..fd..);
addr[0] = 'l';
```
The kernel may say, "okay I see that you want to mmap the file into memory, so I'll reserve some space in your address space that is the length of the file". That means when you write to addr[0] that you are actually writing to the first byte of the file. The kernel can actually do some optimizations too. Instead of loading the file into memory, it may only load pages at a time because if the file is 1024 pages; you may only access 3 or 4 pages making loading the entire file a waste of time (that is why page faults are so powerful! They let the operating system take control of how much you use your files).

## For every mmap

Remember that once you are done `mmap`ping that you `munmap` to tell the operating system that you are no longer using the pages allocated, so the OS can write it back to disk and give you the addresses back in case you need to malloc later.

