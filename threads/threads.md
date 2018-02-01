# Intro to Threads

## What is a thread?
A thread is short for 'thread-of-execution'. It represents the sequence of instructions that the CPU has (and will) execute. To remember how to return from function calls, and to store the values of automatic variables and  parameters a thread uses a stack.

## What is a Lightweight Process (LWP)? How does it relate to threads?

Well for all intents and purposes a thread is a process (meaning that creating a thread is similar to `fork`) except there is **no copying** meaning no copy on write. What this allows is for a process to share the same address space, variables, heap, file descriptors and etc.

The actual system call to create a thread is similar to `fork`; it's `clone`. We won't go into the specifics but you can read the [man pages](http://man7.org/linux/man-pages/man2/clone.2.html) keeping in mind that it is outside the direct scope of this course.

LWP or threads are preferred to forking for a lot of scenarios because there is a lot less overhead creating them. But in some cases (notably python uses this) multiprocessing is the way to make your code faster.

## How does the thread's stack work?
Your main function (and other functions you might call) has automatic variables. We will store them in memory using a stack and keep track of how large the stack is by using a simple pointer (the "stack pointer"). If the thread calls another function, we move our stack pointer down, so that we have more space for parameters and automatic variables. Once it returns from a function, we can move the stack pointer back up to its previous value. We keep a copy of the old stack pointer value - on the stack! This is why returning from a function is very quick - it's easy to 'free' the memory used by automatic variables - we just need to change the stack pointer.

In a multi threaded program, there are multiple stack but only one address space. The pthread library allocates some stack space (either in the heap or using a part of the main program's stack) and uses the `clone` function call to start the thread at that stack address. The total address space may look something like this.

![](https://i.imgur.com/ac2QDwu.png)

## How many threads can my process have?
You can have more than one thread running inside a process. You get the first thread for free! It runs the code you write inside 'main'. If you need more threads you can call `pthread_create` to create a new thread using the pthread library. You'll need to pass a pointer to a function so that the thread knows where to start.

The threads you create all live inside the same virtual memory because they are part of the same process. Thus they can all see the heap, the global variables and the program code etc. Thus you can have two (or more) CPUs working on your program at the same time and inside the same process. It's up to the operating system to assign the threads to CPUs. If you have more active threads than CPUs then the kernel will assign the thread to a CPU for a short duration (or until it runs out of things to do) and then will automatically switch the CPU to work on another thread. 
For example, one CPU might be processing the game AI while another thread is computing the graphics output.

# Simple Usage

## Hello world pthread example
To use pthreads you will need to include `pthread.h` AND you need to compile with `-pthread` (or `-lpthread`) compiler option. This option tells the compiler that your program requires threading support

To create a thread use the function `pthread_create`. This function takes four arguments:
```C
int pthread_create(pthread_t *thread, const pthread_attr_t *attr,
                   void *(*start_routine) (void *), void *arg);
```
* The first is a pointer to a variable that will hold the id of the newly created thread.
* The second is a pointer to attributes that we can use to tweak and tune some of the advanced features of pthreads.
* The third is a pointer to a function that we want to run
* Fourth is a pointer that will be given to our function

The argument `void *(*start_routine) (void *)` is difficult to read! It means a pointer that takes a `void *` pointer and returns a `void *` pointer. It looks like a function declaration except that the name of the function is wrapped with `(* .... )`

Here's the simplest example:
```C
#include <stdio.h>
#include <pthread.h>
// remember to set compilation option -pthread

void *busy(void *ptr) {
// ptr will point to "Hi"
    puts("Hello World");
    return NULL;
}
int main() {
    pthread_t id;
    pthread_create(&id, NULL, busy, "Hi");
    while (1) {} // Loop forever
}
```
If we want to wait for our thread to finish use `pthread_join`
```C
void *result;
pthread_join(id, &result);
```
In the above example, `result` will be `null` because the busy function returned `null`.
We need to pass the address-of result because `pthread_join` will be writing into the contents of our pointer.

# More pthread functions

## How do I create a pthread?
See [Pthreads Part 1](https://github.com/angrave/SystemProgramming/wiki/Pthreads,-Part-1:-Introduction) which introduces `pthread_create` and `pthread_join`

## If I call `pthread_create` twice, how many stacks does my process have?
Your process will contain three stacks - one for each thread. The first thread is created when the process starts, and you created two more. Actually there can be more stacks than this, but let's ignore that complication for now. The important idea is that each thread requires a stack because the stack contains automatic variables and the old CPU PC register, so that it can back to executing the calling function after the function is finished.

## What is the difference between a full process and a thread?
In addition, unlike processes, threads within the same process can share the same global memory (data and heap segments).

## What does `pthread_cancel` do?
Stops a thread. Note the thread may not actually be stopped immediately. For example it can be terminated when the thread makes an operating system call (e.g. `write`).

In practice, `pthread_cancel` is rarely used because it does not give a thread an opportunity to clean up after itself (for example, it may have opened some files).
An alternative implementation is to use a boolean (int) variable whose value is used to inform other threads that they should finish and clean up.

## What is the difference between `exit` and `pthread_exit`?
`exit(42)` exits the entire process and sets the processes exit value.  This is equivalent to `return 42` in the main method. All threads inside the process are stopped.

`pthread_exit(void *)` only stops the calling thread i.e. the thread never returns after calling `pthread_exit`. The pthread library will automatically finish the process if there are no other threads running. `pthread_exit(...)` is equivalent to returning from the thread's function; both finish the thread and also set the return value (void *pointer) for the thread.

Calling `pthread_exit` in the the `main` thread is a common way for simple programs to ensure that all threads finish. For example, in the following program, the  `myfunc` threads will probably not have time to get started.
```C
int main() {
  pthread_t tid1, tid2;
  pthread_create(&tid1, NULL, myfunc, "Jabberwocky");
  pthread_create(&tid2, NULL, myfunc, "Vorpel");
  exit(42); //or return 42;

  // No code is run after exit
}
```
The next two programs will wait for the new threads to finish-
```C
int main() {
  pthread_t tid1, tid2;
  pthread_create(&tid1, NULL, myfunc, "Jabberwocky");
  pthread_create(&tid2, NULL, myfunc, "Vorpel");
  pthread_exit(NULL); 

  // No code is run after pthread_exit
  // However process will continue to exist until both threads have finished
}
```
Alternatively, we join on each thread (i.e. wait for it to finish) before we return from main (or call exit).
```C
int main() {
  pthread_t tid1, tid2;
  pthread_create(&tid1, NULL, myfunc, "Jabberwocky");
  pthread_create(&tid2, NULL, myfunc, "Vorpel");
  // wait for both threads to finish :
  void* result;
  pthread_join(tid1, &result);
  pthread_join(tid2, &result); 
  return 42;
}
```
Note the pthread_exit version creates thread zombies, however this is not a long-running processes, so we don't care.
## How can a thread be terminated?
* Returning from the thread function
* Calling `pthread_exit`
* Cancelling the thread with `pthread_cancel`
* Terminating the process (e.g. SIGTERM); exit(); returning from `main`

## What is the purpose of pthread_join?
* Wait for a thread to finish
* Clean up thread resources
* Grabs the return value of the thread

## What happens if you don't call `pthread_join`?
Finished threads will continue to consume resources. Eventually, if enough threads are created, `pthread_create` will fail.
In practice, this is only an issue for long-running processes but is not an issue for simple, short-lived processes as all thread resources are automatically freed when the process exits.


## Should I use `pthread_exit` or `pthread_join`?
Both `pthread_exit` and `pthread_join` will let the other threads finish on their own (even if called in the main thread). However, only `pthread_join` will return to you when the specified thread finishes. `pthread_exit` does not wait and will immediately end your thread and give you no chance to continue executing.


## Can you pass pointers to stack variables from one thread to another?
Yes. However you need to be very careful about the lifetime of stack variables.
```
pthread_t start_threads() {
  int start = 42;
  pthread_t tid;
  pthread_create(&tid, 0, myfunc, &start); // ERROR!
  return tid;
}
```
The above code is invalid because the function `start_threads` will likely return before `myfunc` even starts. The function passes the address-of `start`, however by the time `myfunc` is executes, `start` is no longer in scope and its address will re-used for another variable.

The following code is valid because the lifetime of the stack variable is longer than the background thread.

```
void start_threads() {
  int start = 42;
  void *result;
  pthread_t tid;
  pthread_create(&tid, 0, myfunc, &start); // OK - start will be valid!
  pthread_join(tid, &result);
}
```

# Intro to Race Conditions

## How can I create ten threads with different starting values.
The following code is supposed to start ten threads with values 0,1,2,3,...9
However, when run prints out `1 7 8 8 8 8 8 8 8 10`! Can you see why?
```C
#include <pthread.h>
void* myfunc(void* ptr) {
    int i = *((int *) ptr);
    printf("%d ", i);
    return NULL;
}

int main() {
    // Each thread gets a different value of i to process
    int i;
    pthread_t tid;
    for(i =0; i < 10; i++) {
        pthread_create(&tid, NULL, myfunc, &i); // ERROR
    }
    pthread_exit(NULL);
}
```
The above code suffers from a `race condition` - the value of i is changing. The new threads start later (in the example output the last thread starts after the loop has finished).

To overcome this race-condition, we will give each thread a pointer to it's own data area. For example, for each thread we may want to store the id, a starting value and an output value:
```C
struct T {
  pthread_t id;
  int start;
  char result[100];
};
```
These can be stored in an array - 
```
struct T *info = calloc(10 , sizeof(struct T)); // reserve enough bytes for ten T structures
```
And each array element passed to each thread - 
```
pthread_create(&info[i].id, NULL, func, &info[i]);
```

## Why are some functions e.g.  asctime,getenv, strtok, strerror  not thread-safe? 
To answer this, let's look at a simple function that is also not 'thread-safe'
```C
char *to_message(int num) {
    char static result [256];
    if (num < 10) sprintf(result, "%d : blah blah" , num);
    else strcpy(result, "Unknown");
    return result;
}
```
In the above code the result buffer is stored in global memory. This is good - we wouldn't want to return a pointer to an invalid address on the stack, but there's only one result buffer in the entire memory. If two threads were to use it at the same time then one would corrupt the other:


Time | Thread 1 | Thread 2| Comments 
-----|----------| --------|------
 1   | to_m(5 ) |         |
 2   |          | to_m(99)| Now both threads will see "Unknown" stored in the result buffer



## What are condition variables, semaphores, mutexes?
These are synchronization locks that are used to prevent race conditions and ensure proper synchronization between threads running in the same program. In addition, these locks are conceptually identical to the primitives used inside the kernel.


## Are there any advantages of using threads over forking processes?
Yes! Sharing information between threads is easy because threads (of the same process) live inside the same virtual memory space.
Also, creating a thread is significantly faster than creating(forking) a process.

## Are there any dis-advantages of using threads over forking processes?
Yes! No- isolation! As threads live inside the same process, one thread has access to the same virtual memory as the other threads. A single thread can terminate the entire process (e.g. by trying to read address zero).

## Can you fork a process with multiple threads?
Yes! However the child process only has a single thread (which is a clone of the thread that called `fork`. We can see this as a simple example, where the background threads never print out a second message in the child process.

```C
#include <pthread.h>
#include <stdio.h>
#include <unistd.h>

static pid_t child = -2;

void *sleepnprint(void *arg) {
  printf("%d:%s starting up...\n", getpid(), (char *) arg);

  while (child == -2) {sleep(1);} /* Later we will use condition variables */

  printf("%d:%s finishing...\n",getpid(), (char*)arg);

  return NULL;  
}
int main() {
  pthread_t tid1, tid2;
  pthread_create(&tid1,NULL, sleepnprint, "New Thread One");
  pthread_create(&tid2,NULL, sleepnprint, "New Thread Two");
  
  child = fork();
  printf("%d:%s\n",getpid(), "fork()ing complete");
  sleep(3);
    
  printf("%d:%s\n",getpid(), "Main thread finished");
  
  pthread_exit(NULL);
  return 0; /* Never executes */
}
```

```
8970:New Thread One starting up...
8970:fork()ing complete
8973:fork()ing complete
8970:New Thread Two starting up...
8970:New Thread Two finishing...
8970:New Thread One finishing...
8970:Main thread finished
8973:Main thread finished
```

In practice, creating threads before forking can lead to unexpected errors because (as demonstrated above) the other threads are immediately terminated when forking. Another thread might have just lock a mutex (e.g. by calling malloc) and never unlock it again. Advanced users may find `pthread_atfork` useful however we suggest you usually try to avoid creating threads before forking unless you fully understand the limitations and difficulties of this approach.

## Are there other reasons where `fork` might be preferable to creating a thread.
Creating separate processes is useful 
* When more security is desired (for example, Chrome browser uses different processes for different tabs)
* When running an existing and complete program then a new process is required (e.g. starting 'gcc')
* When you are running into synchronization primitives and each process is operating on something in the system
 
## How can I find out more?
See the complete example in the [man page](http://man7.org/linux/man-pages/man3/pthread_create.3.html)
And the [pthread reference guide](http://man7.org/linux/man-pages/man7/pthreads.7.html)
ALSO: [Concise third party sample code explaining create, join and exit](http://www.thegeekstuff.com/2012/04/terminate-c-thread/)

# Overview

The next section deals with what happens when pthreads collide, but what if we have each thread do something entirely different, no overlap?

We have found the maximum speedup parallel problems?

## Embarrassingly Parallel Problems 

The study of parallel algorithms has exploded over the past few years. An embarrassingly parallel problem is any problem that needs little effort to turn parallel. A lot of them have some synchronization concepts with them but not always. You already know a parallelizable algorithm, Merge Sort!

```C
void merge_sort(int *arr, size_t len){
     if(len > 1){
     //Mergesort the left half
     //Mergesort the right half
     //Merge the two halves
     }
```

With your new understanding of threads, all you need to do is create a thread for the left half, and one for the right half. Given that your CPU has multiple real cores, you will see a speedup in accordance with [Amdahl's Law](https://en.wikipedia.org/wiki/Amdahl's_law). The time complexity analysis gets interesting here as well. The parallel algorithm runs in O(log^3(n)) running time (because we fancy analysis assuming that we have a lot of cores.

In practice though, we typically do two changes. One, once the array gets small enough, we ditch the parallel mergesort algorithm and do a quicksort or other algorithm that works fast on small arrays (something something cache coherency). The other thing that we know is that CPUs don't have infinite cores. To get around that, we typically keep a worker pool.

## Worker Pool

We know that CPUs have a finite amount of cores. A lot of times we start up a number of threads and give them tasks as they idle.

## Another problem, Parallel Map

Say we want to apply a function to an entire array, one element at a time.

```C

int *map(int (*func)(int), int *arr, size_t len){
    int *ret = malloc(len*sizeof(*arr));
    for(size_t i = 0; i < len; ++i) 
        ret[i] = func(arr[i]);
    return ret;
}
```

Since none of the elements depend on any other element, how would you go about parallelizing this? What do you think would be the best way to split up the work between threads.

## Scheduling

There are a few ways to split up the work.
* static scheduling: break up the problems into fixed size chunks (predetermined) and have each thread work on each of the chunks. This works well when each of the subproblems take roughly the same time because there is no additional overhead. All you need to do is write a loop and give the map function to each subarray.
* dynamic scheduling: as a new problem becomes available have a thread serve it. This is useful when you don't know how long the scheduling will take
* guided scheduling: This is a mix of the above with a mix of the benefits and the tradeoffs. You start with a static scheduling and move slowly to dynamic if needed
* runtime scheduling: You have absolutely no idea how long the problems are going to take. Instead of deciding it yourself, let the program decide what to do!

[source](https://software.intel.com/en-us/articles/openmp-loop-scheduling), but no need to memorize.

## Few Drawbacks

You won't see the speedup right away because of things like cache coherency and scheduling extra threads.

## Other Problems

From [Wikipedia](https://en.wikipedia.org/wiki/Embarrassingly_parallel)
* Serving static files on a webserver to multiple users at once.
* The Mandelbrot set, Perlin noise and similar images, where each point is calculated independently.
* Rendering of computer graphics. In computer animation, each frame may be rendered independently (see parallel rendering).
* Brute-force searches in cryptography.[8] Notable real-world examples include distributed.net and proof-of-work systems used in cryptocurrency.
* BLAST searches in bioinformatics for multiple queries (but not for individual large queries) [9]
* Large scale facial recognition systems that compare thousands of arbitrary acquired faces (e.g., a security or surveillance video via closed-circuit television) with similarly large number of previously stored faces (e.g., a rogues gallery or similar watch list).[10]
* Computer simulations comparing many independent scenarios, such as climate models.
* Evolutionary computation metaheuristics such as genetic algorithms.
* Ensemble calculations of numerical weather prediction.
* Event simulation and reconstruction in particle physics.
* The marching squares algorithm
* Sieving step of the quadratic sieve and the number field sieve.
* Tree growth step of the random forest machine learning technique.
* Discrete Fourier Transform where each harmonic is independently calculated.

# Topics
* pthread lifecycle
* Each thread has a stack
* Capturing return values from a thread
* Using `pthread_join`
* Using `pthread_create`
* Using `pthread_exit`
* Under what conditions will a process exit

# Questions
* What happens when a pthread gets created? (you don't need to go into super specifics)
* Where is each thread's stack?
* How do you get a return value given a `pthread_t`? What are the ways a thread can set that return value? What happens if you discard the return value?
* Why is `pthread_join` important (think stack space, registers, return values)?
* What does `pthread_exit` do under normal circumstances (ie you are not the last thread)? What other functions are called when you call pthread_exit?
* Give me three conditions under which a multithreaded process will exit. Can you think of any more?
* What is an embarrassingly parallel problem?