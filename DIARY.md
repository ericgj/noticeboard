# Noticeboard

An automation and news curation tool for busy organizers 


_12 Aug 2019_

## Devops considerations

I propose the following workflow:

1. Create from cookiecutter template.
2. As a post-gen cookiecutter hook, install build tools:

    virtualenv .env
    . .env/bin/activate && pip install black tox
    git init .
    git add -A && git commit -m "initial commit"
    git branch template
    cp .git-hooks/* .git/hooks/   # run black as pre-commit hook ?
    rm -fr .git-hooks

3. To test locally, `tox`, which runs `flake8` and then 
   `envrun -e config/test.yaml pytest`. Setting up tox.ini for non-package 
   testing.

4. Pre-deploy, `gcloud kms encrypt ...` the secrets files.

5. To deploy, push to production/staging/test branch. This triggers Cloud Build
   to run using a cloudbuild.yaml file or files.  I think perhaps the
   production/staging config files can be parameterized; but the test config
   may need to be a separate file, since it runs integration tests.

  The test deploy looks like:

  1. decrypt secrets
  2. install tox
  3. run tox (which runs linter and tests using the `config/{env}.yaml` env vars)
  4. deploy function with `config/{env}.yaml` env vars. This will automatically
     install requirements.txt on Google infrastructure, etc.
  5. run tox again for an "integration" test environment, which tests hit the 
     actual deployed API (e.g. http endpoint or pubsub), and verify logs and/or
     persisted data.

  So something like this:

    - (gcloud)   gcloud kms decrypt ... --plaintext-file=secrets/service_account.json"
    - (python37) bash -c "virtualenv .env"
    - (python37) bash -c ". .env/bin/activate && pip install tox"
    - (python37) bash -c ". .env/bin/activate && tox -e unit"
    - (gcloud)   gcloud functions deploy ... --env-vars-file=config/$_ENV.yaml
    - (python37) bash -c ". .env/bin/activate && tox -e integration"


## Why tox + virtualenv instead of docker?

One word: speed. Yes it would be nice to get rid of the virtualenv layer and
simply test in isolated docker containers, whether in Cloud Build or locally.
But I tried that, and building the docker containers (as you would have to do
each time you changed your code or tests) is pretty sluggish. 

The other thing that docker shines in for testing is the ability to mount a
network of isolated containers that can talk to each other and the outside 
world (docker compose). But in this case we are building on Google 
infrastructure, not raw containers, so there is no advantage to mounting a
bunch of containers with e.g. no pubsub between them. At least not without some
kind of pubsub emulation layer (which I gather the Cloud Functions nodejs people 
are working on).


