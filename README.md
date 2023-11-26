## Ticket Overflow

### Introduction

This project was developed as a final assessment piece for the [CSSE6400](https://github.com/CSSE6400) software
architecutres course during the final year in my undergraduate software engineering program at The University 
of Queensland (Feb 2023 $-$ Jun 2023).

It functions as a set of REST APIs organised as micro-services to manage all the non-monatry aspects of a
ticketing system, this includes: creating tickets; registering concerts/events; very elemenatry user
management and access; and intergrating external binaries to generate SVG images of the tickets
and of seating allocation at the venue.

### Project Roadmap

#### Migration and Deployment

This section covers all necessary tasks to complete to migrate the submitted version of the code to
my personal repository. This does not include addition of any new features, any additional code 
added will only be used to debug issues found and to aid with deploying to cloud.

- [x] Migration from original course repo to personal repository, this includes inspecting the application and running functionality tests to check if the applications runs **locally**.

- [x] Manual deployment of application to an AWS cloud instance

- [ ] Automating the deployment process with Terraform scripts.

#### Clean Up and Optimisation

As this project was assessment work, it had to be balanced with other course work and the main priority was to produce a functional solution rather than an optimum one, as such many there are many instances where code is repeated, classes and functions poorly organised, poor documentation and the overall approach counters the intended goal of micro-services. 

This section focuses on optimising, reorganising and documenting already present functionality, no new features that veer too far from the initial functions will be added.

- [ ] Database: Redo database storage and access operations, this will mostly involve reorganising present code into neat classes that separate and abstract functionality.

- [ ] SVG Printing: There are a set of celery tasks that handle execution of an external program to generate SVG images of acquired tickets and an seating arrangement availability. This external binary is inefficient in its own right, however, the way the task functions are organised is messy and is prone to future errors and must be corrected.
