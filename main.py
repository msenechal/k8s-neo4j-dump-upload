from fastapi import FastAPI, File, UploadFile, HTTPException
import subprocess
import os
from neo4j import GraphDatabase

app = FastAPI()

NEO4J_URI = os.environ.get("NEO4J_URI")
NEO4J_USERNAME = os.environ.get("NEO4J_USERNAME")
NEO4J_PASSWORD = os.environ.get("NEO4J_PASSWORD")

def create_directory_and_save_file(file, file_name_without_extension):
    # Create a directory with the filename (without extension)
    directory_path = f"./dumps/{file_name_without_extension}"
    os.makedirs(directory_path, exist_ok=True)

    # Create the file in the directory created above
    file_location = f"{directory_path}/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())
    return file_location, directory_path

def get_primary_leader_address():
    # Search for the leader
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    records, summary, keys = driver.execute_query(
        "SHOW DATABASES YIELD name, address, role, writer, currentStatus WHERE name='system' and role='primary' and writer=true and currentStatus='online' RETURN address", 
        database_="system",
    )
    return str(records[0]["address"])

def get_primary_leader_uuid(primary_leader_address):
    # Get the UUID of the Leader
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    records, summary, keys = driver.execute_query(
        "SHOW SERVERS YIELD name, address WHERE address=$primaryLeaderAddress RETURN name", 
        {"primaryLeaderAddress": primary_leader_address},
        database_="system",
    )
    return str(records[0]["name"])

def execute_command(command):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout, stderr, process.returncode

@app.put("/")
async def upload_dump(file: UploadFile = File(...)):
    if not file.filename.endswith('.dump'):
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    file_name_without_extension = os.path.splitext(file.filename)[0]
    file_location, directory_path = create_directory_and_save_file(file, file_name_without_extension)

    primary_leader_address = get_primary_leader_address()
    primary_leader = primary_leader_address.split('.')[0]
    primary_leader_uuid = get_primary_leader_uuid(primary_leader_address)

    # Copy the dump to the Neo4j Leader (This can be skip by using a mounted volume)
    command_cp = f"kubectl cp {directory_path} cluster-demo/{primary_leader}-0:/import/"
    stdout_cp, stderr_cp, returncode_cp = execute_command(command_cp)
    if returncode_cp != 0:
        return {"error": stderr_cp.decode()}

    # Load the dump into the Leader
    command_exec = f"kubectl exec --stdin --tty -n cluster-demo {primary_leader}-0 -- neo4j-admin database load --from-path=/import/{file_name_without_extension} {file_name_without_extension} --expand-commands --verbose"
    stdout_exec, stderr_exec, returncode_exec = execute_command(command_exec)
    if returncode_exec != 0:
        return {"error": stderr_exec.decode()}

    # Seed the cluster with the graph we just loaded
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    records, summary, keys = driver.execute_query(
        "CREATE DATABASE $dbName OPTIONS {existingData: 'use', existingDataSeedInstance: $primaryLeaderUUID}", 
        {"dbName": file_name_without_extension, "primaryLeaderUUID": primary_leader_uuid},
        database_="system",
    )

    # Remove the file and folder
    os.remove(file_location)
    os.removedirs(directory_path)
    
    return {"message": "Your DB has been uploaded and should be available soon"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
