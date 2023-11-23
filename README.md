# k8s-neo4j-dump-upload
This python tool enable users to upload a local Neo4j DB dump (.dump file) to a Neo4j cluster in K8s

## Build the image
```shell
cd k8s-neo4j-dump-upload
docker build -t img/img .
docker run img/img
```
Then push the image to your private registry.

## Deploy in K8s
Changes to make:

- In k8s/deployment.yaml
Change : `your-image-registry/your-image` to the registry/image you pushed in step1

- In k8s/ingress.yaml
Change : `your-hostname.com` to your hostname

Deploying:

```shell
./deploy.sh <your-namespace> <neo4j-uri> <neo4j-username> <neo4j-password>
```

Example:
```shell
./deploy.sh my-namespace neo4j://localhost:7687 neo4j password
```

## Testing
Example for testing the API:
```shell
curl -X PUT -F "file=@test-dumps/movie.dump" https://localhost/uploadDump
```

## Todo
- Using mounted/shared volume so we can remove the kubectl cp step to run faster
- Switching the auth so the script get a token on the Authorization header (either a native using basic64 or an SSO JWT token) and use that token for the neo4j authentication
- Alternatively, could also switch to read the NEO4J_AUTH secret and use it to connect to the cluster
- Use a smaller img based for docker so it is lighter and faster to spin up
- neo4j-uri can probably be deducted from namespace so we could only pass namespace as arg to deploy.sh
- having a flag to overwrite the db if that db already exist