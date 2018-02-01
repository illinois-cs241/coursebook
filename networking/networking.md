Caveat: It should be obvious that  page is *not* a complete description of IP, UDP or TCP! Instead it is a short introduction and is sufficient so that we can build upon these concepts in later lectures.

## What is "IP4" "IP6"?
The following is the "30 second" introduction to internet protocol (IP) - which is the primary way to send packets ("datagrams") of information from one machine to another.

"IP4", or more precisely, "IPv4" is version 4 of the Internet Protocol that describes how to send packets of information across a network from one machine to another . Roughly 95% of all packets on the Internet today are IPv4 packets. A significant limitation of IPv4 is that source and destination addresses are limited to 32 bits (IPv4 was designed at a time when the idea of 4 billion devices connected to the same network was unthinkable - or at least not worth making the packet size larger) 

Each IPv4 packet includes a very small header - typically 20 bytes (more precisely, "octets"), that includes a source and destination address.

Conceptually the source and destination addresses can be split into two: a network number (the upper bits) and the lower bits represent a particular host number on that network.

A newer packet protocol "IPv6" solves many of the limitations of IPv4 (e.g. makes routing tables simpler and 128 bit addresses) however less than 5% of web traffic is IPv6 based.

A machine can have an IPv6 address and an IPv4 address.

## "There's no place like 127.0.0.1"!
A special IPv4 address is `127.0.0.1` also known as localhost. Packets sent to 127.0.0.1 will never leave the machine; the address is specified to be the same machine.

Notice that the 32 bits address is split into 4 octets i.e. each number in the dot notation can be 0-255 inclusive. However IPv4 addresses can also be written as an integer.

## ... and ... "There's no place like 0:0:0:0:0:0:0:1?"
The 128bit localhost address in IPv6 is `0:0:0:0:0:0:0:1` which can be written in its shortened form, `::1`

## What is a port?
To send a datagram (packet) to a host on the Internet using IPv4 (or IPv6) you need to specify the host address and a port. The port is an unsigned 16 bit number (i.e. the maximum port number is 65535).

A process can listen for incoming packets on a particular port. However only processes with super-user (root) access can listen on ports < 1024. Any process can listen on ports 1024 or higher.

An often used port is port 80: Port 80 is used for unencrypted http requests (i.e. web pages).
For example, if a web browser connects to http://www.bbc.com/, then it will be connecting to port 80.

## What is UDP? When is it used?
UDP is a connectionless protocol that is built on top of IPv4 and IPv6. It's very simple to use: Decide the destination address and port and send your data packet! However the network makes no guarantee about whether the packets will arrive.
Packets (aka Datagrams) may be dropped if the network is congested. Packets may be duplicated or arrive out of order.

Between two distant data-centers it's typical to see 3% packet loss.

A typical use case for UDP is when receiving up to date data is more important than receiving all of the data. For example, a game may send continuous updates of player positions. A streaming video signal may send picture updates using UDP

## What is TCP? When is it used?
TCP is a connection-based protocol that is built on top of IPv4 and IPv6 (and therefore can be described as "TCP/IP" or "TCP over IP"). TCP creates a _pipe_ between two machines and abstracts away the low level packet-nature of the Internet: Thus, under most conditions, bytes sent from one machine will eventually arrive at the other end without duplication or data loss. 

TCP will automatically manage resending packets, ignoring duplicate packets, re-arranging out-of-order packets and changing the rate at which packets are sent.

TCP's three way handshake is known as SYN, SYN-ACK, and ACK. The diagram on this page helps with understanding the TCP handshake. [TCP Handshake](http://www.inetdaemon.com/tutorials/internet/tcp/3-way_handshake.shtml)
 
Most services on the Internet today (e.g. a web service) use TCP because it hides the complexity of lower, packet-level nature of the Internet.

## How do I use `getaddrinfo` to convert the hostname into an IP address?

The function `getaddrinfo` can convert a human readable domain name (e.g. `www.illinois.edu`) into an IPv4 and IPv6 address. In fact it will return a linked-list of addrinfo structs:
```C
struct addrinfo {
    int              ai_flags;
    int              ai_family;
    int              ai_socktype;
    int              ai_protocol;
    socklen_t        ai_addrlen;
    struct sockaddr *ai_addr;
    char            *ai_canonname;
    struct addrinfo *ai_next;
};
```

It's very easy to use. For example, suppose you wanted to find out the numeric IPv4 address of a webserver at www.bbc.com. We do this in two stages. First use getaddrinfo to build a linked-list of possible connections. Secondly use `getnameinfo` to convert the binary address into a readable form.

```C
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>

struct addrinfo hints, *infoptr; // So no need to use memset global variables

int main() {
  hints.ai_family = AF_INET; // AF_INET means IPv4 only addresses

  int result = getaddrinfo("www.bbc.com", NULL, &hints, &infoptr);
  if (result) {
    fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(result));
    exit(1);
  }

  struct addrinfo *p;
  char host[256];

  for(p = infoptr; p != NULL; p = p->ai_next) {

    getnameinfo(p->ai_addr, p->ai_addrlen, host, sizeof(host), NULL, 0, NI_NUMERICHOST);
    puts(host);
  }

  freeaddrinfo(infoptr);
  return 0;
}
```
Typical output:
```
212.58.244.70
212.58.244.71
```

## How is www.cs.illinois.edu converted into an IP address?

Magic! No seriously, a system called "DNS" (Domain Name Service) is used. If a machine does not hold the answer locally then it sends a UDP packet to a local DNS server. This server in turn may query other upstream DNS servers. 
## Is DNS secure?

DNS by itself is fast but not secure. DNS requests are not encrypted and susceptible to 'man-in-the-middle' attacks. For example, a coffee shop internet connection could easily subvert your DNS requests and send back different IP addresses for a particular domain

## How do I connect to a TCP server (e.g. web server?)
TODO
There are three basic system calls you need to connect to a remote machine:
```
getaddrinfo -- Determine the remote addresses of a remote host
socket  -- Create a socket
connect  -- Connect to the remote host using the socket and address information
```
The `getaddrinfo` call if successful, creates a linked-list of `addrinfo` structs and sets the given pointer to point to the first one.


The socket call creates an outgoing socket and returns a descriptor (sometimes called a 'file descriptor') that can be used with `read` and `write` etc.In this sense it is the network analog of `open` that opens a file stream - except that we haven't connected the socket to anything yet!

Finally the connect call attempts the connection to the remote machine. We pass the original socket descriptor and also the socket address information which is stored inside the addrinfo structure. There are different kinds of socket address structures (e.g. IPv4 vs IPv6) which can require more memory. So in addition to passing the pointer, the size of the structure is also passed:

```C
// Pull out the socket address info from the addrinfo struct:
connect(sockfd, p->ai_addr, p->ai_addrlen)
```

## How do I free the memory allocated for the linked-list of addrinfo structs?

As part of the clean up code call `freeaddrinfo` on the top-most `addrinfo` struct:
```C
void freeaddrinfo(struct addrinfo *ai);
```

## If getaddrinfo fails can I use `strerror` to print out the error?
No. Error handling with `getaddrinfo` is a little different:
*  The return value _is_ the error code (i.e. don't use `errno`)
* Use `gai_strerror` to get the equivalent short English error text:

```C
int result = getaddrinfo(...);
if(result) { 
   const char *mesg = gai_strerror(result); 
   ...
}
```

## Can I request only IPv4 or IPv6 connection? TCP only?
Yes! Use the addrinfo structure that is passed into `getaddrinfo` to define the kind of connection you'd like.

For example, to specify stream-based protocols over IPv6:
```C
struct addrinfo hints;
memset(&hints, 0, sizeof(hints));

hints.ai_family = AF_INET6; // Only want IPv6 (use AF_INET for IPv4)
hints.ai_socktype = SOCK_STREAM; // Only want stream-based connection
```

## What about code examples that use `gethostbyname`?

The old function `gethostbyname` is deprecated; it's the old way convert a host name into an IP address. The port address still needs to be manually set using htons function. It's much easier to write code to support IPv4 AND IPv6 using the newer `getaddrinfo`

## Is it that easy!?
Yes and no. It's easy to create a simple TCP client - however network communications offers many different levels of abstraction and several attributes and options that can be set at each level of abstraction (for example we haven't talked about `setsockopt` which can manipulate options for the socket).
For more information see this [guide](http://www.beej.us/guide/bgnet/output/html/multipage/getaddrinfoman.html).


## `socket`

`int socket(int domain, int socket_type, int protocol);`

Socket creates a socket with domain (e.g. AF_INET for IPv4 or AF_INET6 for IPv6), `socket_type` is whether to use UDP or TCP or other socket type, `protocol` is an optional choice of protocol configuration (for our examples this we can just leave this as 0 for default). This call creates a socket object in the kernel with which one can communicate with the outside world/network. 
You can use the result of `getaddressinfo` to fill in the `socket` parameters, or provide them manually.

The socket call returns an integer - a file descriptor - and, for TCP clients, you can use it like a regular file descriptor i.e. you can use `read` and `write` to receive or send packets.

TCP sockets are similar to `pipes` except that they allow full duplex communication i.e. you can send and receive data in both directions independently.

## `getaddressinfo`

We saw this in the last section! You're experts at this. 

## `connect`

`int connectok = connect(int sockfd, const struct sockaddr *addr, socklen_t addrlen);`

Pass `connect` the socket file descriptor, the address you want to connect to and the length in bytes of the address structure. To help identify errors and mistakes it is good practice to check the return value of all networking calls, including `connect`

## `read`/`write`

Once we have a successful connection we can read or write like any old file descriptor. Keep in mind if you are connected to a website, you want to conform to the HTTP protocol specification in order to get any sort of meaningful results back. There are libraries to do this, usually you don't connect at the socket level because there are other libraries or packages around it.

The number of bytes read or written may be smaller than expected. Thus it is important to check the return value of read and write. 

## Complete Simple TCP Client Example

```C
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>

int main(int argc, char **argv)
{
	int s;
	int sock_fd = socket(AF_INET, SOCK_STREAM, 0);

	struct addrinfo hints, *result;
	memset(&hints, 0, sizeof(struct addrinfo));
	hints.ai_family = AF_INET; /* IPv4 only */
	hints.ai_socktype = SOCK_STREAM; /* TCP */

	s = getaddrinfo("www.illinois.edu", "80", &hints, &result);
	if (s != 0) {
	        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
        	exit(1);
	}

	if(connect(sock_fd, result->ai_addr, result->ai_addrlen) == -1){
                perror("connect");
                exit(2);
        }

	char *buffer = "GET / HTTP/1.0\r\n\r\n";
	printf("SENDING: %s", buffer);
	printf("===\n");

        // For this trivial demo just assume write() sends all bytes in one go and is not interrupted

	write(sock_fd, buffer, strlen(buffer));


	char resp[1000];
	int len = read(sock_fd, resp, 999);
	resp[len] = '\0';
	printf("%s\n", resp);

    return 0;
}
```

Example output:
```
SENDING: GET / HTTP/1.0

===
HTTP/1.1 200 OK
Date: Mon, 27 Oct 2014 19:19:05 GMT
Server: Apache/2.2.15 (Red Hat) mod_ssl/2.2.15 OpenSSL/1.0.1e-fips mod_jk/1.2.32
Last-Modified: Fri, 03 Feb 2012 16:51:10 GMT
ETag: "401b0-49-4b8121ea69b80"
Accept-Ranges: bytes
Content-Length: 73
Connection: close
Content-Type: text/html

Provided by Web Services at Public Affairs at the University of Illinois
```

## Comment on HTTP request and response
The example above demonstrates a request to the server using Hypertext Transfer Protocol.
A web page (or other resources) are requested using the following request:
```
GET / HTTP/1.0

```
There are four parts (the method e.g. GET,POST,...); the resource (e.g. / /index.html /image.png); the proctocol "HTTP/1.0" and two new lines (\r\n\r\n)


The server's first response line describes the HTTP version used and whether the request is successful using a 3 digit response code:
```
HTTP/1.1 200 OK
```
If the client had requested a non existing file, e.g. `GET /nosuchfile.html HTTP/1.0`
Then the first line includes the response code is the well-known `404` response code:
```
HTTP/1.1 404 Not Found
```


## What is `htons` and when is it used?

Integers can be represented in least significant byte first or most-significant byte first. Either approach is reasonable as long as the machine itself is internally consistent. For network communications we need to standardize on agreed format.

`htons(xyz)` returns the 16 bit unsigned integer 'short' value xyz in network byte order.
`htonl(xyz)` returns the 32 bit unsigned integer 'long' value xyz in network byte order.

These functions are read as 'host to network'; the inverse functions (ntohs, ntohl) convert network ordered byte values to host-ordered ordering. So, is host-ordering  little-endian or big-endian? The answer is - it depends on your machine! It depends on the actual architecture of the host running the code. If the architecture happens to be the same as network ordering then the result of these functions is just the argument. For x86 machines, the host and network ordering _is_ different.

Summary: Whenever you read or write the low level C network structures (e.g. port and address information), remember to use the above functions to ensure correct conversion to/from a machine format. Otherwise the displayed or specified value may be incorrect.

## What are the 'big 4' network calls used to create a server?

The four system calls required to create a TCP server are: `socket`, `bind` `listen` and `accept`. Each has a specific purpose and should be called in the above order

The port information (used by bind) can be set manually (many older IPv4-only C code examples do this), or be created using `getaddrinfo`

We also see examples of setsockopt later too.

## What is the purpose of calling `socket`?

To create a endpoint for networking communication. A new socket by itself is not particularly useful; though we've specified either a packet or stream-based connections it is not bound to a particular network interface or port. Instead socket returns a network descriptor that can be used with later calls to bind,listen and accept.

## What is the purpose of calling `bind`?

The `bind` call associates an abstract socket with an actual network interface and port. It is possible to call bind on a TCP client however it's unusually unnecessary to specify the outgoing port.

## What is the purpose of calling `listen`?

The `listen` call specifies the queue size for the number of incoming, unhandled connections i.e. that have not yet been assigned a network descriptor by `accept`
Typical values for a high performance server are 128 or more.

## Why are server sockets passive?

Server sockets do not actively try to connect to another host; instead they wait for incoming connections. Additionally, server sockets are not closed when the peer disconnects. Instead the client communicates with a separate active socket on the server that is specific to that connection.

Unique TCP connections are identified by the tuple `(source ip, source port, destination ip, destination port)`
It is possible to have multiple connections from a web browser to the same server port (e.g. port 80) because the the source port on each arriving packet is unique. i.e. For a particular server port (e.g. port 80) there can be one passive server socket but multiple active sockets (one for each currently open connection) and the server's operating system maintains a lookup table that associates a unique tuple with active sockets, so that incoming packets can be correctly routed to the correct socket.

## What is the purpose of calling `accept`?

Once the server socket has been initialized the server calls `accept` to wait for new connections. Unlike `socket` `bind` and `listen`, this call will block. i.e. if there are no new connections, this call will block and only return when a new client connects. The returned TCP socket is associated with a particular tuple `(client IP, client port, server IP, server port)` and will be used for all future incoming and outgoing TCP packets that match this tuple. 

Note the `accept` call returns a new file descriptor. This file descriptor is specific to a particular client. It is common programming mistake to use the original server socket descriptor for server I/O and then wonder why networking code has failed.

## What are the gotchas of creating a TCP-server?

+ Using the socket descriptor of the passive server socket (described above)
+ Not specifying SOCK_STREAM requirement for getaddrinfo
+ Not being able to re-use an existing port.
+ Not initializing the unused struct entries
+ The `bind` call will fail if the port is currently in use

Note, ports are per machine- not per process or per user. In other words,  you cannot use port 1234 while another process is using that port. Worse, ports are by default 'tied up' after a process has finished.


## Server code example

A working simple server example is shown below. Note this example is incomplete - for example it does not close either socket descriptor, or free up memory created by `getaddrinfo`

```C
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>
#include <arpa/inet.h>

int main(int argc, char **argv)
{
    int s;
    int sock_fd = socket(AF_INET, SOCK_STREAM, 0);

    struct addrinfo hints, *result;
    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = AF_INET;
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_flags = AI_PASSIVE;

    s = getaddrinfo(NULL, "1234", &hints, &result);
    if (s != 0) {
            fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
            exit(1);
    }

    if (bind(sock_fd, result->ai_addr, result->ai_addrlen) != 0) {
        perror("bind()");
        exit(1);
    }

    if (listen(sock_fd, 10) != 0) {
        perror("listen()");
        exit(1);
    }
    
    struct sockaddr_in *result_addr = (struct sockaddr_in *) result->ai_addr;
    printf("Listening on file descriptor %d, port %d\n", sock_fd, ntohs(result_addr->sin_port));

    printf("Waiting for connection...\n");
    int client_fd = accept(sock_fd, NULL, NULL);
    printf("Connection made: client_fd=%d\n", client_fd);

    char buffer[1000];
    int len = read(client_fd, buffer, sizeof(buffer) - 1);
    buffer[len] = '\0';

    printf("Read %d chars\n", len);
    printf("===\n");
    printf("%s\n", buffer);

    return 0;
}
```

## Why can't my server re-use the port?

By default a port is not immediately released when the server socket is closed. Instead, the port enters a "TIMED-WAIT" state. This can lead to significant confusion during development because the timeout can make valid networking code appear to fail.

 To be able to immediately re-use a port, specify `SO_REUSEPORT` before binding to the port.
```C
int optval = 1;
setsockopt(sfd, SOL_SOCKET, SO_REUSEPORT, &optval, sizeof(optval));

bind(....
```

Here's [an extended stackoverflow introductory discussion of `SO_REUSEPORT`](http://stackoverflow.com/questions/14388706/socket-options-so-reuseaddr-and-so-reuseport-how-do-they-differ-do-they-mean-t).

## What is the difference shutdown and close?

Use the `shutdown` call when you no longer need to read any more data from the socket, write more data, or have finished doing both.
When you shutdown a socket for further writing (or reading) that information is also sent to the other end of the connection. For example if you shutdown the socket for further writing at the server end, then a moment later, a blocked `read` call could return 0 to indicate that no more bytes are expected.

Use `close` when your process no longer needs the socket file descriptor. 

If you `fork`-ed after creating a socket file descriptor, all processes need to close the socket before the socket resources can be re-used.  If you shutdown a socket for further read then all process are be affected because you've changed the socket, not just the file descriptor.

Well written code will `shutdown` a socket before calling `close` it.

## When I re-run my server code it doesn't work! Why?

By default, after a socket is closed the port enters a time-out state during which time it cannot be re-used ('bound to a new socket').

This behavior can be disabled by setting the socket option REUSEPORT before bind-ing to a port:

```C
    int optval = 1;
    setsockopt(sock_fd, SOL_SOCKET, SO_REUSEPORT, &optval, sizeof(optval));

    bind(sock_fd, ...);
```

## Can a TCP client bind to a particular port?

Yes! In fact outgoing TCP connections are automatically bound to an unused port on the client. Usually it's unnecessary to explicitly set the port on the client because the system will intelligently find an unusued port on a reasonable interface (e.g. the wireless card, if currently connected by WiFi connection). However it can be useful if you needed to specifically choose a particular ethernet card, or if a firewall only allows outgoing connections from a particular range of port values.

To explicitly bind to an ethernet interface and port, call `bind` before `connect`

## Who connected to my server?

The `accept` system call can optionally provide information about the remote client, by passing in a sockaddr struct. Different protocols have differently variants of the  `struct sockaddr`, which are different sizes. The simplest struct to use is the `sockaddr_storage` which is sufficiently large to represent all possible types of sockaddr. Notice that C does not have any model of inheritance. Therefore we need to explicitly cast our struct to the 'base type' struct sockaddr.

```C
    struct sockaddr_storage clientaddr;
    socklen_t clientaddrsize = sizeof(clientaddr);
    int client_id = accept(passive_socket,
            (struct sockaddr *) &clientaddr,
             &clientaddrsize);
```

We've already seen `getaddrinfo` that can build a linked list of addrinfo entries (and each one of these can include socket configuration data). What if we wanted to turn socket data into IP and port addresses? Enter `getnameinfo` that can be used to convert a local or remote socket information into a domain name or numeric IP. Similarly the port number can be represented as a service name (e.g. "http" for port 80). In the example below we request numeric versions for the client IP address and client port number.

```C
    socklen_t clientaddrsize = sizeof(clientaddr);
    int client_id = accept(sock_id, (struct sockaddr *) &clientaddr, &clientaddrsize);
    char host[256], port[256];
    getnameinfo((struct sockaddr *) &clientaddr,
          clientaddrsize, host, sizeof(host), port, sizeof(port),
          NI_NUMERICHOST | NI_NUMERICSERV);
```
Todo: Discuss NI_MAXHOST and NI_MAXSERV, and NI_NUMERICHOST 

## getnameinfo Example: What's my IP address?

To obtain a linked list of IP addresses of the current machine use `getifaddrs` which will return a linked list of IPv4 and IPv6 IP addresses (and potentially other interfaces too). We can examine each entry and use `getnameinfo` to print the host's IP address.
The  ifaddrs struct includes the family but does not include the sizeof the struct. Therefore we need to manually determine the struct sized based on the family (IPv4 v IPv6)
```C
 (family == AF_INET) ? sizeof(struct sockaddr_in) : sizeof(struct sockaddr_in6)
```
The complete code is shown below.
```C
    int required_family = AF_INET; // Change to AF_INET6 for IPv6
    struct ifaddrs *myaddrs, *ifa;
    getifaddrs(&myaddrs);
    char host[256], port[256];
    for (ifa = myaddrs; ifa != NULL; ifa = ifa->ifa_next) {
        int family = ifa->ifa_addr->sa_family;
        if (family == required_family && ifa->ifa_addr) {
            if (0 == getnameinfo(ifa->ifa_addr,
                                (family == AF_INET) ? sizeof(struct sockaddr_in) :
                                sizeof(struct sockaddr_in6),
                                host, sizeof(host), port, sizeof(port)
                                 , NI_NUMERICHOST | NI_NUMERICSERV  ))
                puts(host);
            }
        }
```
## What's my machine's IP address (shell version)

Answer: use `ifconfig` (or Windows's ipconfig)
However this command generates a lot of output for each interface, so we can filter the output using grep
```
ifconfig | grep inet

Example output:
	inet6 fe80::1%lo0 prefixlen 64 scopeid 0x1 
	inet 127.0.0.1 netmask 0xff000000 
	inet6 ::1 prefixlen 128 
	inet6 fe80::7256:81ff:fe9a:9141%en1 prefixlen 64 scopeid 0x5 
	inet 192.168.1.100 netmask 0xffffff00 broadcast 192.168.1.255
```

## How do I create a UDP server?
There are a variety of function calls available to send UDP sockets. We will use the newer getaddrinfo to help set up a socket structure.

Remember that UDP is a simple packet-based ('data-gram') protocol ; there is no connection to set up between the two hosts.

First, initialize the hints addrinfo struct to request an IPv6, passive datagram socket.
```C
memset(&hints, 0, sizeof(hints));
hints.ai_family = AF_INET6; // use AF_INET instead for IPv4
hints.ai_socktype =  SOCK_DGRAM;
hints.ai_flags =  AI_PASSIVE;
```

Next, use getaddrinfo to specify the port number (we don't need to specify a host as we are creating a server socket, not sending a packet to a remote host).
```C
getaddrinfo(NULL, "300", &hints, &res);

sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);
bind(sockfd, res->ai_addr, res->ai_addrlen);
```
The port number is <1024, so the program will need `root` privileges. We could have also specified a service name instead of a numeric port value.

So far the calls have been similar to a TCP server. For a stream-based service we would call `listen` and accept. For our UDP-serve we can just start waiting for the arrival of a packet on the socket-

```C
struct sockaddr_storage addr;
int addrlen = sizeof(addr);

// ssize_t recvfrom(int socket, void* buffer, size_t buflen, int flags, struct sockaddr *addr, socklen_t * address_len);

byte_count = recvfrom(sockfd, buf, sizeof(buf), 0, &addr, &addrlen);
```

The addr struct will hold sender (source) information about the arriving packet.
Note the `sockaddr_storage` type is a sufficiently large enough to hold all possible types of socket addresses (e.g. IPv4, IPv6 and other socket types).

## Full Code

```C
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>
#include <arpa/inet.h>

int main(int argc, char **argv)
{
    int s;

    struct addrinfo hints, *res;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_INET6; // INET for IPv4
    hints.ai_socktype =  SOCK_DGRAM;
    hints.ai_flags =  AI_PASSIVE;

    getaddrinfo(NULL, "300", &hints, &res);

    int sockfd = socket(res->ai_family, res->ai_socktype, res->ai_protocol);

    if (bind(sockfd, res->ai_addr, res->ai_addrlen) != 0) {
        perror("bind()");
        exit(1);
    }
    struct sockaddr_storage addr;
    int addrlen = sizeof(addr);

    while(1){
        char buf[1024];
        ssize_t byte_count = recvfrom(sockfd, buf, sizeof(buf), 0, &addr, &addrlen);
        buf[byte_count] = '\0';

        printf("Read %d chars\n", byte_count);
        printf("===\n");
        printf("%s\n", buf);
    }

    return 0;
}
```

### Don't waste time waiting

Normally, when you call `read()`, if the data is not available yet it will wait until the data is ready before the function returns.  When you're reading data from a disk, that delay may not be long, but when you're reading from a slow network connection it may take a long time for that data to arrive, if it ever arrives.  

POSIX lets you set a flag on a file descriptor such that any call to `read()` on that file descriptor will return immediately, whether it has finished or not.  With your file descriptor in this mode, your call to `read()` will start
the read operation, and while it's working you can do other useful work.  This is called "nonblocking" mode,
since the call to `read()` doesn't block.

To set a file descriptor to be nonblocking:
```C
    // fd is my file descriptor
    int flags = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, flags | O_NONBLOCK);
```
For a socket, you can create it in nonblocking mode by adding `SOCK_NONBLOCK` to the second argument to `socket()`:
```C
    fd = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);
```
When a file is in nonblocking mode and you call `read()`, it will return immediately with whatever bytes are available.
Say 100 bytes have arrived from the server at the other end of your socket and you call `read(fd, buf, 150)`.
Read will return immediately with a value of 100, meaning it read 100 of the 150 bytes you asked for.
Say you tried to read the remaining data with a call to `read(fd, buf+100, 50)`, but the last 50 bytes still hadn't
arrived yet.  `read()` would return -1 and set the global error variable **errno** to either
EAGAIN or EWOULDBLOCK.  That's the system's way of telling you the data isn't ready yet.

`write()` also works in nonblocking mode.  Say you want to send 40,000 bytes to a remote server using a socket.
The system can only send so many bytes at a time. Common systems can send about 23,000 bytes at a time. In nonblocking mode, `write(fd, buf, 40000)` would return the number of bytes it was able to
send immediately, or about 23,000.  If you called `write()` right away again, it would return -1 and set errno to
EAGAIN or EWOULDBLOCK. That's the system's way of telling you it's still busy sending the last chunk of data,
and isn't ready to send more yet.

### How do I check when the I/O has finished?

There are a few ways.  Let's see how to do it using *select* and *epoll*.

#### select
```C
    int select(int nfds, 
               fd_set *readfds, 
               fd_set *writefds,
               fd_set *exceptfds, 
               struct timeval *timeout);
```
Given three sets of file descriptors, `select()` will wait for any of those file descriptors to become 'ready'.
* `readfds` - a file descriptor in `readfds` is ready when there is data that can be read or EOF has been reached.
* `writefds` - a file descriptor in `writefds` is ready when a call to write() will succeed.
* `exceptfds` - system-specific, not well-defined.  Just pass NULL for this.

`select()` returns the total number of file descriptors that are ready.  If none of them become
ready during the time defined by *timeout*, it will return 0.  After `select()` returns, the 
caller will need to loop through the file descriptors in readfds and/or writefds to see which
ones are ready. As readfds and writefds act as both input and output parameters, when `select()`
indicates that there are file descriptors which are ready, it would have overwritten them to
reflect only the file descriptors which are ready. Unless it is the caller's intention to call
`select()` only once, it would be a good idea to save a copy of readfds and writefds before
calling it.

```C
    fd_set readfds, writefds;
    FD_ZERO(&readfds);
    FD_ZERO(&writefds);
    for (int i=0; i < read_fd_count; i++)
      FD_SET(my_read_fds[i], &readfds);
    for (int i=0; i < write_fd_count; i++)
      FD_SET(my_write_fds[i], &writefds);

    struct timeval timeout;
    timeout.tv_sec = 3;
    timeout.tv_usec = 0;

    int num_ready = select(FD_SETSIZE, &readfds, &writefds, NULL, &timeout);

    if (num_ready < 0) {
      perror("error in select()");
    } else if (num_ready == 0) {
      printf("timeout\n");
    } else {
      for (int i=0; i < read_fd_count; i++)
        if (FD_ISSET(my_read_fds[i], &readfds))
          printf("fd %d is ready for reading\n", my_read_fds[i]);
      for (int i=0; i < write_fd_count; i++)
        if (FD_ISSET(my_write_fds[i], &writefds))
          printf("fd %d is ready for writing\n", my_write_fds[i]);
    }
```

[For more information on select()](http://pubs.opengroup.org/onlinepubs/9699919799/functions/select.html)

## epoll

*epoll* is not part of POSIX, but it is supported by Linux.  It is a more efficient way to wait for many
file descriptors.  It will tell you exactly which descriptors are ready. It even gives you a way to store
a small amount of data with each descriptor, like an array index or a pointer, making it easier to access
your data associated with that descriptor.

To use epoll, first you must create a special file descriptor with [epoll_create()](http://linux.die.net/man/2/epoll_create).  You won't read or write to this file
descriptor; you'll just pass it to the other epoll_xxx functions and call
close() on it at the end.
```C
    epfd = epoll_create(1);
```
For each file descriptor you want to monitor with epoll, you'll need to add it 
to the epoll data structures 
using [epoll_ctl()](http://linux.die.net/man/2/epoll_ctl) with the `EPOLL_CTL_ADD` option.  You can add any
number of file descriptors to it.
```C
    struct epoll_event event;
    event.events = EPOLLOUT;  // EPOLLIN==read, EPOLLOUT==write
    event.data.ptr = mypointer;
    epoll_ctl(epfd, EPOLL_CTL_ADD, mypointer->fd, &event)
```
To wait for some of the file descriptors to become ready, use [epoll_wait()](http://linux.die.net/man/2/epoll_wait).
The epoll_event struct that it fills out will contain the data you provided in event.data when you
added this file descriptor. This makes it easy for you to look up your own data associated
with this file descriptor.
```C
    int num_ready = epoll_wait(epfd, &event, 1, timeout_milliseconds);
    if (num_ready > 0) {
      MyData *mypointer = (MyData*) event.data.ptr;
      printf("ready to write on %d\n", mypointer->fd);
    }
```
Say you were waiting to write data to a file descriptor, but now you want to wait to read data from it.
Just use `epoll_ctl()` with the `EPOLL_CTL_MOD` option to change the type of operation you're monitoring.
```C
    event.events = EPOLLOUT;
    event.data.ptr = mypointer;
    epoll_ctl(epfd, EPOLL_CTL_MOD, mypointer->fd, &event);
```
To unsubscribe one file descriptor from epoll while leaving others active, use `epoll_ctl()` with the `EPOLL_CTL_DEL` option.
```C
    epoll_ctl(epfd, EPOLL_CTL_DEL, mypointer->fd, NULL);
```
To shut down an epoll instance, close its file descriptor.
```C
    close(epfd);
```
In addition to nonblocking `read()` and `write()`, any calls to `connect()` on a nonblocking socket will also be
nonblocking. To wait for the connection to complete, use `select()` or epoll to wait for the socket to be writable.


## Interesting Blogpost about edge cases with select

https://idea.popcount.org/2017-01-06-select-is-fundamentally-broken/


## What is RPC? 

Remote Procedure Call. RPC is the idea that we can execute a procedure (function) on a different machine. In practice the procedure may execute on the same machine, however it may be in a different context - for example under a different user with different permissions and different lifecycle.

## What is Privilege Separation?

The remote code will execute under a different user and with different privileges from the caller. In practice the remote call may execute with more or fewer privileges than the caller. This in principle can be used to improve the security of a system (by ensuring components operate with least privilege). Unfortunately, security concerns need to be carefully assessed to ensure that RPC mechanisms cannot be subverted to perform unwanted actions. For example, an RPC implementation may implicitly trust any connected client to perform any action, rather than a subset of actions on a subset of the data.

## What is stub code? What is marshalling?

The stub code is the necessary code to hide the complexity of performing a remote procedure call. One of the roles of the stub code is to _marshall_ the necessary data into a format that can be sent as a byte stream to a remote server.

````C
// On the outside 'getHiscore' looks like a normal function call
// On the inside the stub code performs all of the work to send and receive the data to and from the remote machine.

int getHiscore(char* game) {
  // Marshall the request into a sequence of bytes:
  char* buffer;
  asprintf(&buffer,"getHiscore(%s)!", name);

  // Send down the wire (we do not send the zero byte; the '!' signifies the end of the message)
  write(fd, buffer, strlen(buffer) );

  // Wait for the server to send a response
  ssize_t bytesread = read(fd, buffer, sizeof(buffer));

  // Example: unmarshal the bytes received back from text into an int
  buffer[bytesread] = 0; // Turn the result into a C string

  int score= atoi(buffer);
  free(buffer);
  return score;
}
````

## What is server stub code? What is unmarshalling?
The server stub code will receive the request, unmarshall the request into a valid in-memory data call the underlying implementation and send the result back to the caller.

## How do you send an int? float? a struct?  A linked list? A graph?
To implement RPC you need to decide (and document) which conventions you will use to serialize the data into a byte sequence. Even a simple integer has several common choices:
* Signed or unsigned?
* ASCII
* Fixed number of bytes or variable depending on magnitude
* Little or Big endian binary format?

To marshall a struct, decide which fields need to be serialized. It may not be necessary to send all data items (for example, some items may be irrelevant to the specific RPC or can be re-computed by the server from the other data items present).

To marshall a linked list it is unnecessary to send the link pointers- just stream the values. As part of unmarshalling the server can recreate a linked list structure from the byte sequence.

By starting at the head node/vertex, a simple tree can be recursively visited to create a serialized version of the data. A cyclic graph will usually require additional memory to ensure that each edge and vertex is processed exactly once.

## What is an IDL (Interface Description Language)?

Writing stub code by hand is painful, tedious, error prone, difficult to maintain and difficult to reverse engineer the wire protocol from the implemented code. A better approach is specify the data objects, messages and services and automatically generate the client and server code.

A modern example of an Interface Description Language is Google's Protocol Buffer .proto files.

## Complexity and challenges of RPC vs local calls?

Remote Procedure Calls are significantly slower (10x to 100x) and more complex than local calls. An RPC must marshall data into a wire-compatible format. This may require multiple passes through the data structure, temporary memory allocation and transformation of the data representation.

Robust RPC stub code must intelligently handle network failures and versioning. For example, a server may have to process requests from clients that are still running an early version of the stub code.

A secure RPC will need to implement additional security checks (including authentication and authorization), validate data and encrypt communication between the client and host.

## Transferring large amounts of structured data

Let's examine three methods of transferring data using 3 different formats - JSON, XML and Google Protocol Buffers. JSON and XML are text-based protocols. Examples of JSON and XML messages are below.
````xml
<ticket><price currency='dollar'>10</price><vendor>travelocity</vendor></ticket>
````

````javascript
{ 'currency':'dollar' , 'vendor':'travelocity', 'price':'10' }
````

Google Protocol Buffers is an open-source efficient binary protocol that places a strong emphasis on high throughput with low CPU overhead and minimal memory copying. Implementations exist for multiple languages including Go, Python, C++ and C. This means client and server stub code in multiple languages can be generated from the .proto specification file to marshall data to and from a binary stream.

[Google Protocol Buffers](https://developers.google.com/protocol-buffers/docs/overview) reduces the versioning problem by ignoring unknown fields that are present in a message. See the introduction to Protocol Buffers for more information.




# Topics
* IPv4 vs IPv6
* TCP vs UDP
* Packet Loss/Connection Based
* Get address info
* DNS
* TCP client calls
* TCP server calls
* shutdown
* recvfrom
* epoll vs select
* RPC

# Questions
* What is IPv4? IPv6? What are the differences between them?
* What is TCP? UDP? Give me advantages and disadvantages of both of them. When would I use one and not the other?
* Which protocol is connection less and which one is connection based?
* What is DNS? What is the route that DNS takes?
* What does socket do?
* What are the calls to set up a TCP client?
* What are the calls to set up a TCP server?
* What is the difference between a socket shutdown and closing?
* When can you use `read` and `write`? How about `recvfrom` and `sendto`?
* What are some advantages to `epoll` over `select`? How about `select` over `epoll`?
* What is a remote procedure call? When should I use it?
* What is marshalling/unmarshalling? Why is HTTP _not_ an RPC?