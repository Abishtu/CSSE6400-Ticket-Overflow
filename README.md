[![Open in Codespaces](https://classroom.github.com/assets/launch-codespace-7f7980b617ed060a017424585567c406b6ee15c891e84e1186181d67ecf80aa0.svg)](https://classroom.github.com/open-in-codespaces?assignment_repo_id=11012823)

# Harikesha Suresh: 46149318

## Ticket Overflow

I have terraform files that deploy the application to AWS.

Thus far I've done local testing and all conformance and scalability tests work locally, both through the
developement docker container `Dockerfile.dev` and the implentation with `gunicorn` executed through
`Dockerfile`, as present my `docker-compose.yml` build `gunicorn` implementation

You can start a local build with `docker-compose up --build`, it won't do anything now because I'm using
DynamoDB and SQS and removed local table generation code. Aside from that, the application passes all tests
locally
![image](https://github.com/CSSE6400/ticketoverflow-Abishtu/assets/32443198/0e9b4cd3-7358-45d5-b99a-05731dcbc6f3)

To deploy the application, run `./deploy.sh`
