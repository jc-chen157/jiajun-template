


## Setup issue
email: admin@email.com
password: admin

1. ensure using python 3.12, not 3.13,
2. ensure isntall domnion via pip3, check to make sure pip is attached with the venv created
3. ensure to create github token for public repo
4. for macos with M chips, add this
```
DOCKER_DEFAULT_PLATFORM=linux/amd64 domino platform run-compose --github-token <github_token>
```

note: the docker-c will be recrated everytime



## Working with pieces
1. for dependces update, cehck both ./dependceis and requiremnets-test.txt
2. ensure pytest can be succesfully execeuted before pushing to remote 
3. every config.toml change will trigger the validation ci run