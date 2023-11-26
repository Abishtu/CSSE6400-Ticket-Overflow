## Ticket Overflow

### Introduction

This project was developed as a final assessment piece for the ![CSSE6400](https://github.com/CSSE6400) software
architecutres course during the final year in my undergraduate software engineering program at The University 
of Queensland (Feb 2023 $-$ Jun 2023).

It functions as a set of REST APIs organised as micro-services to manage all the non-monatry aspects of a
ticketing system, this includes: creating tickets; registering concerts/events; very elemenatry user
management and access; and intergrating external binaries to generate SVG images of the tickets
and of seating allocation at the venue.

### Project Roadmap

#### Migration and Deployment

This section covers all necceary tasks to complete to migrate the submitted version of the code to
my personal repository. This does not include addition of any new features, any additional code 
added will only be used to debug issues found and to aid with deploying to cloud.


I have terraform files that deploy the application to AWS.

Thus far I've done local testing and all conformance and scalability tests work locally, both through the
developement docker container `Dockerfile.dev` and the implentation with `gunicorn` executed through
`Dockerfile`, as present my `docker-compose.yml` build `gunicorn` implementation

You can start a local build with `docker-compose up --build`, it won't do anything now because I'm using
DynamoDB and SQS and removed local table generation code. Aside from that, the application passes all tests
locally
![image](https://github.com/CSSE6400/ticketoverflow-Abishtu/assets/32443198/0e9b4cd3-7358-45d5-b99a-05731dcbc6f3)

To deploy the application, run `./deploy.sh`
