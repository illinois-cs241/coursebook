# Introduction

Thanks for taking the time to help contribute to the coursebook. We Really appreciate it!
If any of the upcoming sections is confusing, feel free to open an issue, and we'll take a look at it.

Following these guidelines helps accomplish a few things
1. Use the time of other developers and writers wisely
2. Helps in reducing technical debt
3. Keeps professionalism and high quality -- your work will be read by 100s of students every semester!

What kind of contributions are we looking for
* Anything in the issues is fair game!
* Anything you think is an issue is fair game
* We are looking for pictures and other visual explanatory tools that help describe our topics
* We are looking for additional topics as well. These won't be part of the core that students are required to read, but will help if we choose to either bring them in or if students are having trouble understanding without the intuition.
* Additional explanations. Sometimes even though our explanations are

## Philosophy

We provide an open, accessible, first class systems programming textbook that will be free to use forever. Plain and simple.
We want this information to be

* Easily understandable
* In depth when need be
* Skimmable when need be
* Error free with citations
* Highly polished `Perfection is what we expect, excellence will be tolerated`

# Ground Rules

Responsibilities
* Add yourself to AUTHORS.md! We want your work to be recognized :D
* Ensure each piece of code compiles on both the site and the pdf according to our travis builds
* Discuss major changes before implementing
* Be welcoming to systems experts and newbies alike
* Have a professional attitude

# Development environment

## Wiki Dev Environment

To get started with a development environment, make sure you have an up-to-date version of `python3` on your system.
We perfer to use virtualenvironments so that python packages don't conflict. To create one, make sure you have `virtualenv` installed and perform the following commands

```
$ virtualenv -p python3 env
$ source env/bin/activate
(env) $
```

Then to install python dependencies do the following

```
(env) $ python -m pip install -r requirements.txt
```

This will help you build the wiki version of the book. This is the one that gets put into the site. To build that, just run

```
(env) $ mkdir out
(env) $ python _scripts/gen_wiki.py order.yaml out
```

And the markdown will be generated!

## PDF Dev Environment

To get the latex/pdf environment set up, it is a bit easier.
Make sure you have `texlive-full` or the equivalent installed on your machine.

```
$ sudo apt install texlive-full
```

Then to make the whole pdf it is

```
$ make main.pdf
```

To make any chapter it is

```
$ make introc/introc.pdf
```

For those of you unfamiliar to latex, feel free to peruse one of the many online resources. For a scenic tour, I recommend <https://learnxinyminutes.com/docs/latex/>

# Your First Contribution

To start contributing, feel free to take an issue or find a problem, file an issue and start working on it.
For those of you who have never contributed to open source before, here are a few links <http://makeapullrequest.com/> and <http://www.firsttimersonly.com/>
If a maintainer asks you to "rebase" your PR, they're saying that a lot of code has changed, and that you need to update your branch so it's easier to merge.

# Getting started

Want to contribute? Afraid of latex or python? Don't be!

If you want to contribute, all you need to do is
1. Fork
2. Make the changes by
    1. Going to the appropriate chapter
    2. Make changes either online or on the command line
    3. Make a PR
3. The PR will be cleared up and on build, a new version of the couresbook will be released and deployed!

If you want to actually contribute to the code, you'll need `texlive-full` and `python3`

```
sudo apt install texlive-full
python3 -V
```

Install all of the requirements in the requirements.txt file at the top of the repository.
We recommend doing this in a virtualenvironment as to not mess up other packages

```
virtualenv -p python3.5 env
source env/bin/activate
pip install -r requirements.txt
```

To generate a wiki version, it is a simple as

```
mkdir out
python3 _scripts/gen_wiki.py order.yaml out
```

To generate the pdf it is as simple as

```
make
```

If you find a security vulnerability, do NOT open an issue. Email angrave@illinois.edu instead.

## Filing a Content Issue

Template:

> When filing an Content, make sure to answer these five questions:
>
> 1. What problem does the new content solve?
> 2. How many changes to the existing book will it need?
> 3. What will need to be done?
> 4. Will this be addition or core information?

## Filing a bug

Template

> When filing an Content, make sure to answer these five questions:
>
> 1. What problem is there?
> 2. What are the minimal reproducable steps?
> 3. What versions of python3, packages, pandoc, latex compiler do you have?
> 4. What system are you building on?

## Reviews

After a feature and PR is made, add a contributor to the PR to review your contributions.
Once we approve, we are good to merge.
