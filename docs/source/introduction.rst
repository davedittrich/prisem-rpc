.. _introduction:

Introduction
============

This repository contains a working set of remote procedure call (RPC)
client/server based services intended to support a distributed
system event log and network flow collection and query facility. They
are written so as to act as a front-end to system-specific commands
and communicate using a generic request and response mechanism that
is language independent, operating system independent, and secure.

The security in this model is obtained by restricting the functionality
of the underlying commands that are invoked at the command line through
the supported request elements, rather than simply passing user-supplied
input directly to a command line.

