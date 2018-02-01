## What is a Resource Allocation Graph?
A resource allocation graph tracks which resource is held by which process and which process is waiting for a resource of a particular type. It is very powerful and simple tool to illustrate how interacting  processes can deadlock. If a process is _using_ a resource, an arrow is drawn from the resource node to the process node. If a process is _requesting_ a resource, an arrow is drawn from the process node to the resource node.


If there is a cycle in the Resource Allocation Graph and each resource in the cycle provides only one instance, then the processes will deadlock. For example, if process 1 holds resource A, process 2 holds resource B and process 1 is waiting for B and process 2 is waiting for A, then process 1 and 2 process will be deadlocked.

Here's another example, that shows Processes 1 and 2 acquiring resources 1 and 2 while process 3 is waiting to acquire both resources. In this example there is no deadlock because there is no circular dependency.

![ResourceAllocationGraph-Ex1.png](https://raw.githubusercontent.com/wiki/angrave/SystemProgramming/ResourceAllocationGraph-Ex1.png)


## Deadlock!

A lot of times, we don't know the specific order that a resource may be acquired so we can draw the graph directed.

![](http://i.imgur.com/V16FfnX.png)

As a possibility matrix. Then we can draw arrows and see if there is a directed version that would lead us to a deadlock.

![RAG Deadlock](http://i.imgur.com/6duq0PD.png)

Consider the following resource allocation graph (assume that the processes ask for exclusive access to the file). If you have a bunch of processes running and they request resources and the operating system ends up in this state, you deadlock! You may not see this because the operating system may **preempt** some processes breaking the cycle but there is still a change that your three lonely processes could deadlock. You can also make these kind of graphs with `make` and rule dependencies (with our parmake MP for example).

![](http://cs241.cs.illinois.edu/images/ColorfulDeadlock.svg)

## Coffman conditions
There are four _necessary_ and _sufficient_ conditions for deadlock. These are known as the Coffman conditions.

* Mutual Exclusion
* Circular Wait
* Hold and Wait
* No pre-emption

If you break any of them, you cannot have deadlock!

All of these conditions are required for deadlock, so let's discuss each one in turn. First the easy ones-
* Mutual Exclusion: The resource cannot be shared
* Circular Wait: There exists a cycle in the Resource Allocation Graph. There exists a set of processes {P1,P2,...} such that P1 is waiting for resources held by P2, which is waiting for P3,..., which is waiting for P1.
* Hold and Wait: A process acquires an incomplete set of resources and holds onto them while waiting for the other resources.
* No pre-emption: Once a process has acquired a resource, the resource cannot be taken away from a process and the process will not voluntarily give up a resource.

## Breaking the Coffman Conditions

Two students need a pen and paper:
* The students share a pen and paper. Deadlock is avoided because Mutual Exclusion was not required.
* The students both agree to grab the pen before grabbing the paper. Deadlock is avoided because there cannot be a circular wait.
* The students grab both the pen and paper in one operation ("Get both or get none"). Deadlock is avoided because there is no _Hold and Wait_
* The students are friends and will ask each other to give up a held resource. Deadlock is avoided because pre-emption is allowed.


## Livelock
Livelock is _not_ deadlock-

Consider the following 'solution'
* The students will put down one held resource if they are unable to pick up the other resource within 10 seconds. This solution avoids deadlock however it may suffer from livelock.

Livelock occurs when a process continues to execute but is unable to make progress.
In practice Livelock may occur because the programmer has taken steps to avoid deadlock. In the above example, in a busy system, the student will continually release the first resource because they are never able to obtain the second resource. The system is not deadlock (the student process is still executing) however it's not making any progress either.

## Deadlock Prevention/Avoidance vs Deadlock Detection

Deadlock prevention is making sure that deadlock cannot happen, meaning that you break a coffman condition. This works the best inside a single program and the software engineer making the choice to break a certain coffman condition. Consider the [Banker's Algorithm](https://en.wikipedia.org/wiki/Banker's_algorithm). It is another algorithm for deadlock avoidance. The whole implementation is outside the scope of this class, just know that there are more generalized algorithms for operating systems.

Deadlock detection on the other hand is allowing the system to enter a deadlocked state. After entering, the system uses the information that it has to break deadlock. As an example, consider multiple processes accessing files. The operating system is able to keep track of all of the files/resources through file descriptors at some level (either abstracted through an API or directly). If the operating system detects a directed cycle in the operating system file descriptor table it may break one process' hold (through scheduling for example) and let the system proceed.

## Dining Philosophers

The Dining Philosophers problem is a classic synchronization problem. Imagine I invite N (let's say 5) philosophers to a meal. We will sit them at a table with 5 chopsticks (one between each philosopher). A philosopher alternates between wanting to eat or think. To eat the philosopher must pick up the two chopsticks either side of their position (the original problem required each philosopher to have two forks). However these chopsticks are shared with his neighbor.

![5DiningPhilosophers](https://raw.githubusercontent.com/wiki/angrave/SystemProgramming/5DiningPhilosophers.png)

Is it possible to design an efficient solution such that all philosophers get to eat? Or, will some philosophers starve, never obtaining a second chopstick? Or will all of them deadlock? For example, imagine each guest picks up the chopstick on their left and then waits for the chopstick on their right to be free. Oops - our philosophers have deadlocked!


# Backstory
<img src="https://upload.wikimedia.org/wikipedia/commons/7/7b/An_illustration_of_the_dining_philosophers_problem.png" height="500px" width="500px">

So you have your philosophers sitting around a table all wanting to eat some pasta (or whatever that is) and they are really hungry. Each of the philosophers are essentially the same, meaning that each philosopher has the same instruction set based on the other philosopher ie you can't tell every even philosopher to do one thing and every odd philosopher to do another thing.

# Failed Solutions
## Left-Right Deadlock
What do we do? Let's try a simple solution

````C
void* philosopher(void* forks){
     info phil_info = forks;
     pthread_mutex_t* left_fork = phil_info->left_fork;
     pthread_mutex_t* right_fork = phil_info->right_fork;
     while(phil_info->simulation){
          pthread_mutex_lock(left_fork);
          pthread_mutex_lock(right_fork);
          eat(left_fork, right_fork);
          pthread_mutex_unlock(left_fork);
          pthread_mutex_unlock(right_fork);
     }
}
````

But this runs into a problem! What if everyone picks up their left fork and is waiting on their right fork? We have deadlocked the program. It is important to note that deadlock doesn't happen all the time and the probability that this solution deadlocks goes down as the number of philosophers goes up. What is really important to note is that eventually that this solution will deadlock, letting threads starve which is bad.

## Trylock? More like livelock
So now you are thinking about breaking one of the coffman conditions. We have
- Mutual Exclusion
- No Preemption
- Hold and wait
- Circular Wait

Well we can't have two philosophers use a fork at the same time, mutual exclusion is out of the picture. In our current, simple model, we can't have the philosopher let go of the mutex lock once he/she has a hold of it, so we will take this solution out right now -- there are some notes at the bottom of the page about this solution. Let's break Hold and Wait!
````C
void* philosopher(void* forks){
     info phil_info = forks;
     pthread_mutex_t* left_fork = phil_info->left_fork;
     pthread_mutex_t* right_fork = phil_info->right_fork;
     while(phil_info->simulation){
          pthread_mutex_lock(left_fork);
          int failed = pthread_mutex_trylock(right_fork);
          if(!failed){
               eat(left_fork, right_fork);
               pthread_mutex_unlock(right_fork);
          }
          pthread_mutex_unlock(left_fork);
     }
}
````

Now our philosopher picks up the left fork and tries to grab the right. If it's available, they eat. If it's not available, they put the left fork down and try again. No deadlock!

But, there is a problem. What if all the philosophers pick up their left at the same time, try to grab their right, put their left down, pick up their left, try to grab their right.... We have now livelocked our solution! Our poor philosopher are still starving, so let's give them some proper solutions.

# Viable Solutions

## Arbitrator (Naive and Advanced).

The naive arbitrator solution is have one arbitrator (a mutex for example). Have each of the philosopher ask the arbitrator for permission to eat. This solution allows one philosopher to eat at a time. When they are done, another philosopher can ask for permission to eat.

This prevents deadlock because there is no circular wait! No philosopher has to wait on any other philosopher.

The advanced arbitrator solution is to implement a class that determines if the philosopher's forks are in the arbitrator's possession. If they are, they give them to the philosopher, let him eat, and take the forks back. This has the added bonus of being able to have multiple philosopher eat at the same time.

### Problems:
- These solutions are slow
- They have a single point of failure, the arbitrator making it a bottleneck
- The arbitrator needs to also be fair, and be able to determine deadlock in the second solution
- In practical systems, the arbitrator tends to give the forks repeatedly to philosophers that just ate because of process scheduling

## Leaving the Table (Stallings' Solution)
Why does the first solution deadlock? Well there are n philosophers and n chopsticks. What if there is only 1 philsopher at the table? Can we deadlock? No. 

How about 2 philsophers? 3? ... You can see where this is going. Stallings' solutions says to remove philosophers from the table until deadlock is not possible -- think about what the magic number of philosophers at the table is. The way to do this in actual system is through semaphores and letting a certain number of philosopher through.

### Problems:
- The solution requires a lot of context switching which is very expensive for the CPU
- You need to know about the number of resources before hand in order to only let that number of philosophers
- Again priority is given to the processes who have already eaten.

## Partial Ordering (Dijkstra's Solution)
This is Dijkstra's solution (he was the one to propose this problem on an exam). Why does the first solution deadlock? Dijkstra thought that the last philosopher who picks up his left fork (causing the solution to deadlock) should pick up his right. He accomplishes it by number the forks 1..n, and tells each of the philosopher to pick up his lower number fork.

Let's run through the deadlock condition again. Everyone tries to pick up their lower number fork first. Philosopher 1 gets fork 1, Philosopher 2 gets fork 2, and so on until we get to Philosopher n. They have to choose between fork 1 and n. fork 1 is already held up by philosopher 1, so they can't pick up that fork, meaning he won't pick up fork n. We have broken circular wait! Meaning deadlock isn't possible.

### Problems:
- The philosopher needs to know the set of resources in order before grabbing any resources.
- You need to define a partial order to all of the resources.
- Prioritizes philosopher who have already eaten.

## Advanced Solutions

There are many more advanced solutions a non-exhaustive list includes
- Clean/Dirty Forks (Chandra/Misra Solution)
- Actor Model (other Message passing models)
- Super Arbitrators (Complicated pipelines)

# Topics
Coffman Conditions
Resource Allocation Graphs
Dining Philosophers
* Failed DP Solutions
* Livelocking DP Solutions
* Working DP Solutions: Benefits/Drawbacks

# Questions
* What are the Coffman Conditions?
* What do each of the Coffman conditions mean? (e.g. can you provide a definition of each one)
* Give a real life example of breaking each Coffman condition in turn. A situation to consider: Painters, Paint, Paintbrushes etc. How would you assure that work would get done?
* Be able to identify when Dining Philosophers code causes a deadlock (or not).
For example, if you saw the following code snippet which Coffman condition is not satisfied?
```C
// Get both locks or none.
pthread_mutex_lock( a );
if( pthread_mutex_trylock( b ) ) { /*failed*/
   pthread_mutex_unlock( a );
   ...
}
```


* If one thread calls
```C
  pthread_mutex_lock(m1) // success
  pthread_mutex_lock(m2) // blocks
```
and another threads calls
```C
  pthread_mutex_lock(m2) // success
  pthread_mutex_lock(m1) // blocks
```
What happens and why? What happens if a third thread calls `pthread_mutex_lock(m1)` ?

* How many processes are blocked? As usual assume that a process is able to complete if it is able to acquire all of the resources listed below.
     * P1 acquires R1
     * P2 acquires R2
     * P1 acquires R3
     * P2 waits for R3
     * P3 acquires R5
     * P1 waits for R4
     * P3 waits for R1
     * P4 waits for R5
     * P5 waits for R1

(Draw out the resource graph!)