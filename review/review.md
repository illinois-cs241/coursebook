The final exam will likely include multiple choice questions that test your mastery of the following.

```
CSP (critical section problems)
HTTP
SIGINT
TCP
TLB
Virtual Memory
arrays
barrier
c strings
chmod
client/server
coffman conditions
condition variables
context switch
deadlock
dining philosophers
epoll
exit
file I/O
file system representation
fork/exec/wait
fprintf
free
heap allocator
heap/stack
inode vs name
malloc
mkfifo
mmap
mutexes
network ports
open/close
operating system terms
page fault
page tables
pipes
pointer arithmetic
pointers
printing (printf)
producer/consumer
progress/mutex
race conditions
read/write
reader/writer
resource allocation graphs
ring buffer
scanf 
buffering
scheduling
select
semaphores
signals
sizeof
stat
stderr/stdout
symlinks
thread control (_create, _join, _exit)
variable initializers
variable scope
vm thrashing
wait macros
write/read with errno, EINTR and partial data
```

# C
# Memory and Strings
## Q1.1
In the example below, which variables are guaranteed to print the value of zero?
```C
int a;
static int b;

void func() {
   static int c;
   int d;
   printf("%d %d %d %d\n",a,b,c,d);
}
```
## Q 1.2
In the example below, which variables are guaranteed to print the value of zero?
```C
void func() {
   int* ptr1 = malloc( sizeof(int) );
   int* ptr2 = realloc(NULL, sizeof(int) );
   int* ptr3 = calloc( 1, sizeof(int) );
   int* ptr4 = calloc( sizeof(int) , 1);
   
   printf("%d %d %d %d\n",*ptr1,*ptr2,*ptr3,*ptr4);
}
```
## Q 1.3
Explain the error in the following attempt to copy a string.
```C
char* copy(char*src) {
 char*result = malloc( strlen(src) ); 
 strcpy(result, src); 
 return result;
}
```
## Q 1.4
Why does the following attempt to copy a string sometimes work and sometimes fail?

```C
char* copy(char*src) {
 char*result = malloc( strlen(src) +1 ); 
 strcat(result, src); 
 return result;
}
```
## Q 1.4
Explain the two errors in the following code that attempts to copy a string.
```C
char* copy(char*src) {
 char result[sizeof(src)]; 
 strcpy(result, src); 
 return result;
}
```
## Q 1.5
Which of the following is legal?
```C
char a[] = "Hello"; strcpy(a, "World");
char b[] = "Hello"; strcpy(b, "World12345", b);
char* c = "Hello"; strcpy(c, "World");
```

## Q 1.6
Complete the function pointer typedef to declare a pointer to a function that takes a void* argument and returns a void*. Name your type 'pthread_callback'
```C
typedef ______________________;
```
## Q 1.7
In addition to the function arguments what else is stored on a thread's stack?

## Q 1.8
Implement a version of `char* strcat(char*dest, const char*src)` using only `strcpy`  `strlen` and pointer arithmetic
```C
char* mystrcat(char*dest, const char*src) {

  ? Use strcpy strlen here

  return dest;
}
```
## Q 1.9
Implement version of size_t strlen(const char*) using a loop and no function calls.
```C
size_t mystrlen(const char*s) {

}
```
## Q 1.10
Identify the three bugs in the following implementation of `strcpy`.
```C
char* strcpy(const char* dest, const char* src) {
  while(*src) { *dest++ = *src++; }
  return dest;
}
```



# Printing
## Q 2.1
Spot the two errors!
```
fprintf("You scored 100%");
```
# Formatting and Printing to a file
## Q 3.1
Complete the following code to print to a file. Print the name, a comma and the score to the file 'result.txt'
```C
char* name = .....;
int score = ......
FILE *f = fopen("result.txt",_____);
if(f) {
    _____
}
fclose(f);
```
# Printing to a string
## Q 4.1

How would you print the values of variables a,mesg,val and ptr to a string? Print a as an integer, mesg as C string, val as a double val and ptr as a hexadecimal pointer. You may assume the mesg points to a short C string(<50 characters).
Bonus: How would you make this code more robust or able to cope with?
```C
char* toString(int a, char*mesg, double val, void* ptr) {
   char* result = malloc( strlen(mesg) + 50);
    _____
   return result;
}
```

# Input parsing
## Q 5.1
Why should you check the return value of sscanf and scanf?
## Q 5.2
Why is 'gets' dangerous?

## Q 5.3
Write a complete program that uses `getline`. Ensure your program has no memory leaks.

## Heap memory
When would you use calloc not malloc? 
When would realloc be useful?

(Todo - move this question to another page)
What mistake did the programmer make in the following code? Is it possible to fix it i) using heap memory? ii) using global (static) memory?
```C
static int id;

char* next_ticket() {
  id ++;
  char result[20];
  sprintf(result,"%d",id);
  return result;
}
```


## Q1
Is the following code thread-safe? Redesign the following code to be thread-safe. Hint: A mutex is unnecessary if the message memory is unique to each call.

```C
static char message[20];
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

void *format(int v) {
  pthread_mutex_lock(&mutex);
  sprintf(message, ":%d:" ,v);
  pthread_mutex_unlock(&mutex);
  return message;
}
```
## Q2
Which one of the following does not cause a process to exit?
* Returning from the pthread's starting function in the last running thread.
* The original thread returning from main.
* Any thread causing a segmentation fault.
* Any thread calling `exit`.
* Calling `pthread_exit` in the main thread with other threads still running.


## Q3
Write a mathematical expression for the number of "W" characters that will be printed by the following program. Assume a,b,c,d are small positive integers. Your answer may use a 'min' function that returns its lowest valued argument.

```C
unsigned int a=...,b=...,c=...,d=...;

void* func(void* ptr) {
  char m = * (char*)ptr;
  if(m == 'P') sem_post(s);
  if(m == 'W') sem_wait(s);
  putchar(m);
  return NULL;
}

int main(int argv, char** argc) {
  sem_init(s,0, a);
  while(b--) pthread_create(&tid, NULL, func, "W"); 
  while(c--) pthread_create(&tid, NULL, func, "P"); 
  while(d--) pthread_create(&tid, NULL, func, "W"); 
  pthread_exit(NULL); 
  /*Process will finish when all threads have exited */
}
```

## Q4
Complete the following code. The following code is supposed to print alternating `A` and `B`. It represents two threads that take turns to execute.  Add condition variable calls to `func` so that the waiting thread does not need to continually check the `turn` variable. Q: Is pthread_cond_broadcast necessary or is pthread_cond_signal sufficient?
```C
pthread_cond_t cv = PTHREAD_COND_INITIALIZER;
pthread_mutex_t m = PTHREAD_MUTEX_INITIALIZER;

void* turn;

void* func(void* mesg) {
  while(1) {
// Add mutex lock and condition variable calls ...

    while(turn == mesg) { 
        /* poll again ... Change me - This busy loop burns CPU time! */ 
    }

    /* Do stuff on this thread */
    puts( (char*) mesg);
    turn = mesg;
    
  }
  return 0;
}

int main(int argc, char** argv){
  pthread_t tid1;
  pthread_create(&tid1, NULL, func, "A");
  func("B"); // no need to create another thread - just use the main thread
  return 0;
}
```

## Q5
Identify the critical sections in the given code. Add mutex locking to make the code thread safe. Add condition variable calls so that `total` never becomes negative or above 1000. Instead the call should block until it is safe to proceed. Explain why `pthread_cond_broadcast` is necessary.
```C
int total;
void add(int value) {
 if(value < 1) return;
 total += value;
}
void sub(int value) {
 if(value < 1) return;
 total -= value;
}
```

## Q6
A non-threadsafe data structure has `size()` `enq` and `deq` methods. Use condition variable and mutex lock to complete the thread-safe, blocking versions.
```C
void enqueue(void* data) {
  // should block if the size() would become greater than 256
  enq(data);
}
void* dequeue() {
  // should block if size() is 0
  return deq();
}
```

## Q7
Your startup offers path planning using latest traffic information. Your overpaid intern has created a non-threadsafe data structure with two functions: `shortest` (which uses but does not modify the graph) and `set_edge` (which modifies the graph).
```C
graph_t* create_graph(char* filename); // called once

// returns a new heap object that is the shortest path from vertex i to j
path_t* shortest(graph_t* graph, int i, int j); 

// updates edge from vertex i to j
void set_edge(graph_t* graph, int i, int j, double time); 
  
```
For performance, multiple threads must be able to call `shortest` at the same time but the graph can only be modified by one thread when no threads other are executing inside `shortest` or `set_edge`.
 
Use mutex lock and condition variables to implement a reader-writer solution. An incomplete attempt is shown below. Though this attempt is threadsafe (thus sufficient for demo day!), it does not allow multiple threads to calculate `shortest` path at the same time and will not have sufficient throughput.
```C
path_t* shortest_safe(graph_t* graph, int i, int j) {
  pthread_mutex_lock(&m);
  path_t* path = shortest(graph, i, j);
  pthread_mutex_unlock(&m);
  return path;
}
void set_edge_safe(graph_t* graph, int i, int j, double dist) {
  pthread_mutex_lock(&m);
  set_edge(graph, i, j, dist);
  pthread_mutex_unlock(&m);
}
```
> Note thread-programming synchronization problems are on a separate wiki page. This page focuses on conceptual topics.
> Question numbers subject to change
 
## Q1
What do each of the Coffman conditions mean? (e.g. can you provide a definition of each one)
* Hold and wait
* Circular wait
* No pre-emption
* Mutual exclusion

## Q2
Give a real life example of breaking each Coffman condition in turn. A situation to consider: Painters, paint and paint brushes.
Hold and wait
Circular wait
No pre-emption
Mutual exclusion

## Q3
Identify when Dining Philosophers code causes a deadlock (or not). For example, if you saw the following code snippet which Coffman condition is not satisfied?

```
// Get both locks or none.
pthread_mutex_lock( a );
if( pthread_mutex_trylock( b ) ) { /*failed*/
   pthread_mutex_unlock( a );
   ...
}
```

## Q4
How many processes are blocked?

* P1 acquires R1
* P2 acquires R2
* P1 acquires R3
* P2 waits for R3
* P3 acquires R5
* P1 acquires R4
* P3 waits for R1
* P4 waits for R5
* P5 waits for R1

## Q5 
How many of the following statements are true for the reader-writer problem?

* There can be multiple active readers
* There can be multiple active writers
* When there is an active writer the number of active readers must be zero
* If there is an active reader the number of active writers must be zero
* A writer must wait until the current active readers have finished


## Q1
What are the following and what is their purpose?
* Translation Lookaside Buffer
* Physical Address
* Memory Management Unit
* The dirty bit

## Q2
How do you determine how many bits are used in the page offset?

## Q3
20 ms after a context switch the TLB contains all logical addresses used by your numerical code which performs main memory access 100% of the time. What is the overhead (slowdown) of a two-level page table compared to a single-level page table?

## Q4
Explain why the TLB must be flushed when a context switch occurs (i.e. the CPU is assigned to work on a different process).

> Question numbers subject to change

## Q1
Fill in the blanks to make the following program print 123456789. If `cat` is given no arguments it simply prints its input until EOF. Bonus: Explain why the `close` call below is necessary.
```C
int main() {
  int i = 0;
  while(++i < 10) {
    pid_t pid = fork();
    if(pid == 0) { /* child */
      char buffer[16];
      sprintf(buffer, ______,i);
      int fds[ ______];
      pipe( fds);
      write( fds[1], ______,______ ); // Write the buffer into the pipe
      close(  ______ );
      dup2( fds[0],  ______);
      execlp( "cat", "cat",  ______ );
      perror("exec"); exit(1);
    }
    waitpid(pid, NULL, 0);
  }
  return 0;
}
```

## Q2
Use POSIX calls `fork` `pipe` `dup2` and `close` to implement an autograding program. Capture the standard output of a child process into a pipe. The child process should `exec` the program `./test` with no additional arguments (other than the process name). In the parent process read from the pipe: Exit the parent process as soon as the captured output contains the ! character. Before exiting the parent process send SIGKILL to the child process. Exit 0 if the output contained a !. Otherwise if the child process exits causing the pipe write end to be closed, then exit with a value of 1. Be sure to close the unused ends of the pipe in the parent and child process

## Q3 (Advanced)
This advanced challenge uses pipes to get an "AI player" to play itself until the game is complete.
The program `tictactoe` accepts a line of input - the sequence of turns made so far, prints the same sequence followed by another turn, and then exits. A turn is specified using two characters. For example "A1" and "C3" are two opposite corner positions. The string `B2A1A3` is a game of 3 turns/plys. A valid response is `B2A1A3C1` (the C1 response blocks the diagonal B2 A3 threat). The output line may also include a suffix `-I win` `-You win` `-invalid` or `-draw`
Use pipes to control the input and output of each child process created. When the output contains a `-`, print the final output line (the entire game sequence and the result) and exit.


> Question numbers subject to change

## Q1
Write a function that uses fseek and ftell to replace the middle character of a file with an 'X'
```C
void xout(char* filename) {
  FILE *f = fopen(filename, ____ );
  


}
```
## Q2
In an `ext2` filesystem how many inodes are read from disk to access the first byte of the file `/dir1/subdirA/notes.txt` ? Assume the directory names and inode numbers in the root directory (but not the inodes themselves) are already in memory.

## Q3
In an `ext2` filesystem what is the minimum number of disk blocks that must be read from disk to access the first byte of the file `/dir1/subdirA/notes.txt` ? Assume the directory names and inode numbers in the root directory and all inodes are already in memory.

## Q4
In an `ext2` filesystem with 32 bit addresses and 4KB disk blocks, an inodes that can store 10 direct disk block numbers. What is the minimum file size required to require an single indirection table? ii) a double direction table?

## Q5
Fix the shell command `chmod` below to set the permission of a file `secret.txt`  so that the owner can read,write,and execute permissions the group can read and everyone else has no access.
```
chmod 000 secret.txt
```

* [Wiki w/Interactive MC Questions](http://angrave.github.io/SystemProgramming/networkingreviewquestions.html)
* See [Coding questions](#coding-questions)
* See [Short answer questions](#short-answer-questions)
* See [MP Wearables](https://courses.engr.illinois.edu/cs241/mps/mp7/) Food For Thought questions


# Short answer questions
## Q1
What is a socket?

## Q2 

What is special about listening on port 1000 vs port 2000?

- Port 2000 is twice as slow as port 1000
- Port 2000 is twice as fast as port 1000
- Port 1000 requires root privileges
- Nothing


## Q3 
Describe one significant difference between IPv4 and IPv6

## Q4
When and why would you use ntohs?

## Q5
If a host address is 32 bits which IP scheme am I most likely using? 128 bits?

## Q6
Which common network protocol is packet based and may not successfully deliver the data?

## Q7
Which common protocol is stream-based and will resend data if packets are lost?

## Q8
What is the SYN ACK ACK-SYN handshake?

## Q9
Which one of the following is NOT a feature of TCP? 
- Packet re-ordering
- Flow control
- Packet re-tranmission
- Simple error detection
- Encryption

## Q10
What protocol uses sequence numbers? What is their initial value? And why?

## Q11
What are the minimum network calls are required to build a TCP server? What is their correct order?

## Q12
What are the minimum network calls are required to build a TCP client? What is their correct order?

## Q13
When would you call bind on a TCP client?

## Q14 
What is the purpose of
socket
bind
listen
accept
?

## Q15
Which of the above calls can block, waiting for a new client to connect?

## Q16
What is DNS? What does it do for you? Which of the CS241 network calls will use it for you?

## Q17
For getaddrinfo, how do you specify a server socket?

## Q18
Why may getaddrinfo generate network packets?

## Q19
Which network call specifies the size of the allowed backlog?

## Q20
Which network call returns a new file descriptor?

## Q21
When are passive sockets used?

## Q22
When is epoll a better choice than select? When is select a better choice than epoll?

## Q23
Will  `write(fd, data, 5000)`  always send 5000 bytes of data? When can it fail?

## Q24 
How does Network Address Translation (NAT) work? 


## Q25
@MCQ
Assuming a network has a 20ms Transmit Time between Client and Server, how much time would it take to establish a TCP Connection?
20 ms
40 ms 
100 ms
60 ms @ANS
3 Way Handshake @EXP
@END


## Q26
What are some of the differences between HTTP 1.0 and HTTP 1.1? How many ms will it take to transmit 3 files from server to client if the network has a 20ms transmit time? How does the time taken differ between HTTP 1.0 and HTTP 1.1?


# Coding questions
## Q 2.1

Writing to a network socket may not send all of the bytes and may be interrupted due to a signal. Check the return value of `write` to implement `write_all` that will repeatedly call `write` with any remaining data. If `write` returns -1 then immediately return -1 unless the `errno` is `EINTR` - in which case repeat the last `write` attempt. You will need to use pointer arithmetic.
```C
// Returns -1 if write fails (unless EINTR in which case it recalls write
// Repeated calls write until all of the buffer is written.
ssize_t write_all(int fd, const char *buf, size_t nbyte) {
  ssize_t nb = write(fd, buf, nbyte);
  return nb;
}
```

## Q 2.2
Implement a multithreaded TCP server that listens on port 2000. Each thread should read 128 bytes from the client file descriptor and echo it back to the client, before closing the connection and ending the thread.

## Q 2.3
Implement a UDP server that listens on port 2000. Reserve a buffer of 200 bytes. Listen for an arriving packet. Valid packets are 200 bytes or less and start with four bytes 0x65 0x66 0x67 0x68. Ignore invalid packets. For valid packets add the value of the fifth byte as an unsigned value to a running total and print the total so far. If the running total is greater than 255 then exit.

## Give the names of two signals that are normally generated by the kernel

## Give the name of a signal that can not be caught by a signal 

## Why is it unsafe to call any function (something that it is not signal handler safe) in a signal handler?

Coding Questions

Write brief code that uses SIGACTION and a SIGNALSET to create a SIGALRM handler.

