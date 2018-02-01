# Wait Macros

## Can I find out the exit value of my child?

You can find the lowest 8 bits of the child's exit value (the return value of `main()` or value included in `exit()`): Use the "Wait macros" - typically you will use "WIFEXITED" and "WEXITSTATUS" . See `wait`/`waitpid` man page for more information).
```C
int status;
pid_t child = fork();
if (child == -1) return 1; //Failed
if (child > 0) { /* I am the parent - wait for the child to finish */
  pid_t pid = waitpid(child, &status, 0);
  if (pid != -1 && WIFEXITED(status)) {
     int low8bits = WEXITSTATUS(status);
     printf("Process %d returned %d" , pid, low8bits);
  }
} else { /* I am the child */
 // do something interesting
  execl("/bin/ls", "/bin/ls", ".", (char *) NULL); // "ls ."
}
```

A process can only have 256 return values, the rest of the bits are informational.

## Bit Shifting

Note there is no need to memorize this, this is just a high level overview of how information is stored inside the status variables

From Android source code:
```C
/* If WIFEXITED(STATUS), the low-order 8 bits of the status. */

#define __WEXITSTATUS(status) (((status) & 0xff00) >> 8)

/* If WIFSIGNALED(STATUS), the terminating signal. */

#define __WTERMSIG(status) ((status) & 0x7f)

/* If WIFSTOPPED(STATUS), the signal that stopped the child. */

#define __WSTOPSIG(status) __WEXITSTATUS(status)

/* Nonzero if STATUS indicates normal termination. */

#define __WIFEXITED(status) (__WTERMSIG(status) == 0)
```

The kernel has an internal way of keeping track of signaled, exited, or stopped. That API is abstracted so that that the kernel developers are free to change at will.

## Being careful.

Remember that the the macros only make sense if the precondition is met. Meaning that a process' exit status won't be defined if the process is signaled. The macros will not do the checking for you, so it's up to the programming to make sure the logic checks out.

# Signals

## What's a signal?

A signal is a construct provided to us by the kernel. It allows one process to asynchronously send a signal (think a message) to another process. If that process wants to accept the signal, it can, and then, for most signals, can decide what to do with that signal. Here is a short list (non comprehensive) of signals.

|   Name   |             Default Action             | Usual Use Case |
|----------|----------------------------------------|--------------------------------|
| SIGINT   | Terminate Process (Can be caught)      | Tell the process to stop nicely |
| SIGQUIT  | Terminate Process (Can be caught)      | Tells the process to stop harshly |
| SIGSTOP  | Stop Process (Cannot be caught)        | Stops the process to be continued |
| SIGCONT  | Continues a Process                    | Continues to run the process |
| SIGKILL  | Terminate Process (Cannot be caught)   | You want your process gone |

## When are signals generated?

* When the user sends a signal. For example, you are at the terminal, and you send `CTRL-C`
* When a system event happens. For example, you get a `SIGCHILD` after forking to notice when one of your children have exited.
* When another program sends it. For example, when you execute `kill -9 PID`, it sends `SIGKILL`
* When an appropriate hardware interrupt is triggered. For example, if you access a page that you aren't supposed to, the hardware generates a segfault interrupt which gets intercepted by the kernel. The kernel finds the process that caused this and sends a software interrupt signal `SIGSEGV`.

## Can I pause my child?

Yes ! You can temporarily pause a running process by sending it a SIGSTOP signal.
If it succeeds it will freeze a process; i.e. the process will not be allocated any more CPU time.

To allow a process to resume execution send it the SIGCONT signal.

For example,
Here's program that slowly prints a dot every second, up to 59 dots.
```C
#include <unistd.h>
#include <stdio.h>
int main() {
  printf("My pid is %d\n", getpid() );
  int i = 60;
  while(--i) { 
    write(1, ".",1);
    sleep(1);
  }
  write(1, "Done!",5);
  return 0;
}
```
We will first start the process in the background (notice the & at the end).
Then send it a signal from the shell process by using the kill command.
```
>./program &
My pid is 403
...
>kill -SIGSTOP 403
>kill -SIGCONT 403
```

## How do I kill/stop/suspend my child from C?
In C, send a signal to the child using `kill` POSIX call,
```C
kill(child, SIGUSR1); // Send a user-defined signal
kill(child, SIGSTOP); // Stop the child process (the child cannot prevent this)
kill(child, SIGTERM); // Terminate the child process (the child can prevent this)
kill(child, SIGINT); // Equivalent to CTRL-C (by default closes the process)
```

As we saw above there is also a kill command available in the shell
e.g. get a list of running processes and then terminate process 45 and process 46
```
ps
kill -l 
kill -9 45
kill -s TERM 46
```
## How can I detect "CTRL-C" and clean up gracefully?

We will return to signals later on - this is just a short introduction. On a Linux system, see `man -s7 signal` if you are interested in finding out more (for example a list of system and library calls that are async-signal-safe).

There are strict limitations on the executable code inside a signal handler. Most library and system calls are not 'async-signal-safe' - they may not be used inside a signal handler because they are not re-entrant safe. In a single-threaded program, signal handling momentarily interrupts the program execution to execute the signal handler code instead. Suppose your original program was interrupted while executing the library code of `malloc` ;  the memory structures used by malloc will not be in a consistent state. Calling `printf` (which uses `malloc`) as part of the signal handler is unsafe and will result in "undefined behavior" i.e. it is no longer a useful,predictable program. In practice your program might crash, compute or generate incorrect results or stop functioning ("deadlock"), depending on exactly what your program was executing when it was interrupted to execute the signal handler code.


One common use of signal handlers is to set a boolean flag that is occasionally polled (read) as part of the normal running of the program. For example,
```C
int pleaseStop ; // See notes on why "volatile sig_atomic_t" is better

void handle_sigint(int signal) {
  pleaseStop = 1;
}

int main() {
  signal(SIGINT, handle_sigint);
  pleaseStop = 0;
  while ( ! pleaseStop) { 
     /* application logic here */ 
   }
  /* cleanup code here */
}
```
The above code might appear to be correct on paper. However, we need to provide a hint to the compiler and to the CPU core that will execute the `main()` loop. We need to prevent a compiler optimization: The expression `! pleaseStop` appears to be a loop invariant i.e. true forever, so can be simplified to `true`.  Secondly, we need to ensure that the value of `pleaseStop` is not cached using a CPU register and instead always read from and written to main memory. The `sig_atomic_t` type implies that all the bits of the variable can be read or modified as an "atomic operation" - a single uninterruptable operation. It is impossible to read a value that is composed of some new bit values and old bit values.

By specifying `pleaseStop` with the correct type `volatile sig_atomic_t` we can write portable code where the main loop will be exited after the signal handler returns. The `sig_atomic_t` type can be as large as an `int` on most modern platforms but on embedded systems can be as small as a `char` and only able to represent (-127 to 127) values.
```C
volatile sig_atomic_t pleaseStop;
```
Two examples of this pattern can be found in "COMP" a terminal based 1Hz 4bit computer (https://github.com/gto76/comp-cpp/blob/1bf9a77eaf8f57f7358a316e5bbada97f2dc8987/src/output.c#L121).
Two boolean flags are used. One to mark the delivery of `SIGINT` (CTRL-C), and gracefully shutdown the program, and the other to mark `SIGWINCH` signal to detect terminal resize and redraw the entire display. 

# Signals In Depth

## How can I learn more about signals?

The linux man pages discusses signal system calls in section 2. There is also a longer article in section 7 (though not in OSX/BSD):
```
man -s7 signal
```

## Signal Terminology
* Generated - The signal is being created in the kernel by the kill system call.
* Pending - Not delivered yet but soon to be delivered
* Blocked - Not delivered because no signal disposition lets the signal be delivered
* Delivered - Delivered to the process, the action described is being taken
* Caught - When the process stops a signal from destroying it and does something else with it instead

## What is a process's signal disposition?
For each process, each signal has a disposition which means what action will occur when a signal is delivered to the process. For example, the default disposition SIGINT is to terminate it. The signal disposition can be changed by calling signal() (which is simple but not portable as there are subtle variations in its implementation on different POSIX architectures and also not recommended for multi-threaded programs) or `sigaction` (discussed later). You can imagine the processes' disposition to all possible signals as a table of function pointers entries (one for each possible signal).

The default disposition for signals can be to ignore the signal, stop the process, continue a stopped process, terminate the process, or terminate the process and also dump a 'core' file. Note a core file is a representation of the processes' memory state that can be inspected using a debugger.

## Can multiple signals be queued?

No - however it is possible to have signals that are in a pending state. If a signal is pending, it means it has not yet been delivered to the process. The most common reason for a signal to be pending is that the process (or thread) has currently blocked that particular signal.

If a particular signal, e.g. SIGINT, is pending then it is not possible to queue up the same signal again.

It _is_ possible to have more than one signal of a different type in a pending state. For example SIGINT and SIGTERM signals may be pending (i.e. not yet delivered to the target process)

## How do I block signals?
Signals can be blocked (meaning they will stay in the pending state) by setting the process signal mask or, when you are writing a multi-threaded program, the thread signal mask.

# Disposition in Threads/Children

## What happens when creating a new thread?
The new thread inherits a copy of the calling thread's mask
```C
pthread_sigmask( ... ); // set my mask to block delivery of some signals
pthread_create( ... ); // new thread will start with a copy of the same mask
```

## What happens when forking?

The child process inherits a copy of the parent's signal dispositions. In other words, if you have installed a SIGINT handler before forking, then the child process will also call the handler if a SIGINT is delivered to the child.

Note pending signals for the child are _not_ inherited during forking.

## What happens during exec ?
Both the signal mask and the signal disposition carries over to the exec-ed program. [https://www.gnu.org/software/libc/manual/html_node/Executing-a-File.html#Executing-a-File](Source) Pending signals are preserved as well.  Signal handlers are reset, because the original handler code has disappeared along with the old process.

## What happens during fork ?
The child process inherits a copy of the parent process's signal disposition and a copy of the parent's signal mask.

For example if `SIGINT` is blocked in the parent it will be blocked in the child too.
For example if the parent installed a handler (call-back function) for SIG-INT then the child will also perform the same behavior.

Pending signals however are not inherited by the child.

## How do I block signals in a single-threaded program?
Use `sigprocmask`! With sigprocmask you can set the new mask, add new signals to be blocked to the process mask, and unblock currently blocked signals. You can also determine the existing mask (and use it for later) by passing in a non-null value for oldset.

```
int sigprocmask(int how, const sigset_t *set, sigset_t *oldset);`
```

From the Linux man page of sigprocmask,
```
SIG_BLOCK: The set of blocked signals is the union of the current set and the set argument.
SIG_UNBLOCK: The signals in set are removed from the current set of blocked signals. It is permissible to attempt to unblock a signal which is not blocked.
SIG_SETMASK: The set of blocked signals is set to the argument set.

```
The sigset type behaves as a bitmap, except functions are used rather than explicitly setting and unsetting bits using & and |. 

It is a common error to forget to initialize the signal set before modifying one bit. For example,
```C
sigset_t set, oldset;
sigaddset(&set, SIGINT); // Ooops!
sigprocmask(SIG_SETMASK, &set, &oldset)
```
Correct code initializes the set to be all on or all off. For example,
```C
sigfillset(&set); // all signals
sigprocmask(SIG_SETMASK, &set, NULL); // Block all the signals!
// (Actually SIGKILL or SIGSTOP cannot be blocked...)

sigemptyset(&set); // no signals 
sigprocmask(SIG_SETMASK, &set, NULL); // set the mask to be empty again
```

## How do I block signals in a multi-threaded program?
Blocking signals is similar in multi-threaded programs to single-threaded programs:
* Use pthread_sigmask instead of sigprocmask
* Block a signal in all threads to prevent its asynchronous delivery

The easiest method to ensure a signal is blocked in all threads is to set the signal mask in the main thread before new threads are created

```C
sigemptyset(&set);
sigaddset(&set, SIGQUIT);
sigaddset(&set, SIGINT);
pthread_sigmask(SIG_BLOCK, &set, NULL);

// this thread and the new thread will block SIGQUIT and SIGINT
pthread_create(&thread_id, NULL, myfunc, funcparam);
```

Just as we saw with sigprocmask, pthread_sigmask includes a 'how' parameter that defines how the signal set is to be used:
```C
pthread_sigmask(SIG_SETMASK, &set, NULL) - replace the thread's mask with given signal set
pthread_sigmask(SIG_BLOCK, &set, NULL) - add the signal set to the thread's mask
pthread_sigmask(SIG_UNBLOCK, &set, NULL) - remove the signal set from the thread's mask
```

## How are pending signals delivered in a multi-threaded program?
A signal is delivered to any signal thread that is not blocking that signal.

If the two or more threads can receive the signal then which thread will be interrupted is arbitrary!

## How do I send a signal to a process from the shell?
You already know one way to send a `SIG_INT` just type `CTRL-C` 
From the shell you can use `kill` (if you know the process id) and `killall` (if you know the process name)
```
# First let's use ps and grep to find the process we want to send a signal to
$ ps au | grep myprogram
angrave  4409   0.0  0.0  2434892    512 s004  R+    2:42PM   0:00.00 myprogram 1 2 3

#Send SIGINT signal to process 4409 (equivalent of `CTRL-C`)
$ kill -SIGINT 4409

#Send SIGKILL (terminate the process)
$ kill -SIGKILL 4409
$ kill -9 4409
```

`killall` is similar except that it matches by program name. The next two example, sends a `SIGINT` and then `SIGKILL` to terminate the processes that are running `myprogram`
```
# Send SIGINT (SIGINT can be ignored)
$ killall -SIGINT myprogram

# SIGKILL (-9) cannot be ignored! 
$ killall -9 myprogram
```
## How do I send a signal to a process from the running C program?
Use `raise` or `kill`
```C
int raise(int sig); // Send a signal to myself!
int kill(pid_t pid, int sig); // Send a signal to another process
```
For non-root processes, signals can only be sent to processes of the same user i.e. you cant just SIGKILL my processes! See kill(2) i.e. man -s2 for more details.
 

## How do I send a signal to a specific thread?
Use `pthread_kill`
```C
int pthread_kill(pthread_t thread, int sig)
```

In the example below, the newly created thread executing `func` will be interrupted by `SIGINT`

```C
pthread_create(&tid, NULL, func, args);
pthread_kill(tid, SIGINT);
pthread_kill(pthread_self(), SIGKILL); // send SIGKILL to myself
```

## Will `pthread_kill( threadid, SIGKILL)` kill the process or thread?
It will kill the entire process. Though individual threads can set a signal mask, the signal disposition (the table of handlers/action performed for each signal) is *per-proces*s not *per-thread*. This means 
`sigaction` can be called from any thread because you will be setting a signal handler for all threads in the process.

## How do I catch (handle) a signal ?
You can choose a handle pending signals asynchronously or synchronously.

Install a signal handler to asynchronously handle signals use `sigaction` (or, for simple examples, `signal` ).

To synchronously catch a pending signal use `sigwait` (which blocks until a signal is delivered) or `signalfd` (which also blocks and provides a file descriptor that can be `read()` to retrieve pending signals).

See `Signals, Part 4` for an example of using `sigwait`

## How and why do I use `sigaction` ?

You should use `sigaction` instead of `signal` because it has better defined semantics. `signal` on different operating system does different things which is **bad** `sigaction` is more portable and is better defined for threads if need be.

To change the "signal disposition" of a process - i.e. what happens when a signal is delivered to your process - use `sigaction`

You can use system call `sigaction` to set the current handler for a signal or read the current signal handler for a particular signal.

```C
int sigaction(int signum, const struct sigaction *act, struct sigaction *oldact);
```
The sigaction struct includes two callback functions (we will only look at the 'handler' version), a signal mask and a flags field -
```C
struct sigaction {
               void     (*sa_handler)(int);
               void     (*sa_sigaction)(int, siginfo_t *, void *);
               sigset_t   sa_mask;
               int        sa_flags;
}; 
```
## How do I convert a `signal` call into the equivalent `sigaction` call?

Suppose you installed a signal handler for the alarm signal,
```C
signal(SIGALRM, myhandler);
```

The equivalent `sigaction` code is:
```C
struct sigaction sa; 
sa.sa_handler = myhandler;
sigemptyset(&sa.sa_mask);
sa.sa_flags = 0; 
sigaction(SIGALRM, &sa, NULL)
```

However, we typically may also set the mask and the flags field. The mask is a temporary signal mask used during the signal handler execution. The SA_RESTART flag will automatically restart some (but not all) system calls that otherwise would have returned early (with EINTR error). The latter means we can simplify the rest of code somewhat because a restart loop may no longer be required.

```C
sigfillset(&sa.sa_mask);
sa.sa_flags = SA_RESTART; /* Restart functions if  interrupted by handler */     
```

## How do I use sigwait?

Sigwait can be used to read one pending signal at a time. `sigwait` is used to synchronously wait for signals, rather than handle them in a callback. A typical use of sigwait in a multi-threaded program is shown below. Notice that the thread signal mask is set first (and will be inherited by new threads). This prevents signals from being _delivered_ so they will remain in a pending state until sigwait is called. Also notice the same set sigset_t variable is used by sigwait - except rather than setting the set of blocked signals it is being used as the set of signals that sigwait can catch and return.

One advantage of writing a custom signal handling thread (such as the example below) rather than a callback function is that you can now use many more C library and system functions that otherwise could not be safely used in a signal handler because they are not async signal-safe.
 
Based on `http://pubs.opengroup.org/onlinepubs/009695399/functions/pthread_sigmask.html`
```C
static sigset_t   signal_mask;  /* signals to block         */

int main (int argc, char *argv[])
{
    pthread_t sig_thr_id;      /* signal handler thread ID */
    sigemptyset (&signal_mask);
    sigaddset (&signal_mask, SIGINT);
    sigaddset (&signal_mask, SIGTERM);
    pthread_sigmask (SIG_BLOCK, &signal_mask, NULL);

    /* New threads will inherit this thread's mask */
    pthread_create (&sig_thr_id, NULL, signal_thread, NULL);

    /* APPLICATION CODE */
    ...
}

void *signal_thread (void *arg)
{
    int       sig_caught;    /* signal caught       */

    /* Use same mask as the set of signals that we'd like to know about! */
    sigwait(&signal_mask, &sig_caught);
    switch (sig_caught)
    {
    case SIGINT:     /* process SIGINT  */
        ...
        break;
    case SIGTERM:    /* process SIGTERM */
        ...
        break;
    default:         /* should normally not happen */
        fprintf (stderr, "\nUnexpected signal %d\n", sig_caught);
        break;
    }
}
```

# Topics
* Signals
* Signal Handler Safe
* Signal Disposition
* Signal States
* Pending Signals when Forking/Exec
* Signal Disposition when Forking/Exec
* Raising Signals in C
* Raising Signals in a multithreaded program

# Questions
* What is a signal?
* How are signals served under UNIX? (Bonus: How about Windows?)
* What does it mean that a function is signal handler safe
* What is a process Signal Disposition?
* How do I change the signal disposition in a single threaded program? How about multithreaded?
* Why sigaction vs signal?
* How do I asynchronously and synchronously catch a signal?
* What happens to pending signals after I fork? Exec?
* What happens to my signal disposition after I fork? Exec?
