# Blue-green switch script (bash)
# Usage: ./switch-to-green.sh   or   ./switch-to-blue.sh

set -e

NAMESPACE=flowforge-prod
SERVICE=flowforge

if [ "$1" = "green" ]; then
  echo "Switching service to green track..."
  kubectl patch service $SERVICE -n $NAMESPACE --type='json' \
    -p='[{"op": "replace", "path": "/spec/selector/track", "value": "green"}]'
  echo "Service now points to green. Verify with: kubectl get svc $SERVICE -n $NAMESPACE -o yaml"
elif [ "$1" = "blue" ]; then
  echo "Switching service back to blue track..."
  kubectl patch service $SERVICE -n $NAMESPACE --type='json' \
    -p='[{"op": "replace", "path": "/spec/selector/track", "value": "blue"}]'
  echo "Rolled back to blue."
else
  echo "Usage: $0 [blue|green]"
  exit 1
fi
