#!/bin/bash
# Author: Morgan Senechal
# Created: 23/11/2023
# Modified: -
# Version: 1.0

NAMESPACE=${1:-'my-namespace'}
NEO4J_URI=${2:-'neo4j://localhost:7687'}
NEO4J_USERNAME=${3:-'neo4j'}
NEO4J_PASSWORD=${4:-'password'}

echo "⏳ - Starting deployment of KGS-UPLOAD in ${NAMESPACE}"

echo "⏳ - Deploying KGS-UPLOAD Deployment ..." 
kgsuploadDeployment=`cat "k8s/deployment.yaml" | \
            sed "s|{{NAMESPACE}}|$NAMESPACE|g" | \
            sed "s|{{NEO4J_URI}}|$NEO4J_URI|g" | \
            sed "s|{{NEO4J_USERNAME}}|$NEO4J_USERNAME|g" | \
            sed "s|{{NEO4J_PASSWORD}}|$NEO4J_PASSWORD|g"`
echo "$kgsuploadDeployment" | kubectl apply -n $NAMESPACE -f -
echo "✅ - KGS-UPLOAD Deployment deployed." 

echo "⏳ - Deploying KGS-UPLOAD Service ..." 
kgsuploadService=`cat "k8s/service.yaml" | \
            sed "s/{{NAMESPACE}}/$NAMESPACE/g"`
echo "$kgsuploadService" | kubectl apply -n $NAMESPACE -f -
echo "✅ - KGS-UPLOAD Service deployed." 

echo "⏳ - Deploying KGS-UPLOAD Ingress ..." 
kgsuploadIngress=`cat "k8s/ingress.yaml" | \
            sed "s/{{NAMESPACE}}/$NAMESPACE/g"`
echo "$kgsuploadIngress" | kubectl apply -n $NAMESPACE -f -
echo "✅ - KGS-UPLOAD Ingress deployed." 

echo "⏳ - Deploying KGS-UPLOAD ClusterRole ..." 
kgsuploadClusterRole=`cat "k8s/cluster-role.yaml" | \
            sed "s/{{NAMESPACE}}/$NAMESPACE/g"`
echo "$kgsuploadClusterRole" | kubectl apply -n $NAMESPACE -f -
echo "✅ - KGS-UPLOAD ClusterRole deployed." 